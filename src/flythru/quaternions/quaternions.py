# -*- coding: utf-8 -*-
import numpy as np
import copy
from XCoreModeling import Vec3


def interpolate_keyframes(keyframes, num, mode="cubic"):
    if mode == "linear":
        res = []
        for f1, f2 in zip(keyframes[0:-1], keyframes[1:]):
            for t in np.linspace(0, 1, num, endpoint=False):
                if t == 0.0:
                    keyframe = f1
                else:
                    # q = t*np.array(f2['Orientation']) + (1-t)*np.array(f1['Orientation'])
                    # proper quaternion interpolation
                    q = slerp(f2["Orientation"], f1["Orientation"], 1 - t)
                    keyframe = as_keyframe(
                        orbit_center=t * Vec3(f2["OrbitCenter"])
                        + (1.0 - t) * Vec3(f1["OrbitCenter"]),
                        orientation=q,
                        distance=t * f2["Distance"] + (1 - t) * f1["Distance"],
                    )
                res.append(keyframe)
        return res
    elif mode == "cubic":
        q_array = [keyframe["Orientation"] for keyframe in keyframes]
        d_array = [keyframe["Distance"] for keyframe in keyframes]
        c_array = [Vec3(keyframe["OrbitCenter"]) for keyframe in keyframes]

        t_array = np.linspace(0, 1, num=len(keyframes) * num)

        q_interp = [quat_spline(q_array, t) for t in t_array]
        d_interp = [lin_interp(d_array, t) for t in t_array]
        c_interp = [lin_interp(c_array, t) for t in t_array]

        for q in q_array:
            print(q)
        for t, q in zip(t_array, q_interp):
            print(f"{t} {q}")

        return [as_keyframe(c, q, d) for c, q, d in zip(c_interp, q_interp, d_interp)]

    else:
        raise NotImplementedError("Unknown interpolation mode: {}".format(mode))


def lin_interp(data_array, t):
    """linear interpolation of an array of scalars or an array of Vec3"""
    assert t >= 0 and t <= 1
    if t == 0:
        return data_array[0]
    elif t == 1:
        return data_array[-1]
    for j in range(1, len(data_array)):
        alpha = eval_alpha(
            t, j, len(data_array)
        )  # shifting global percentage value to interval percentage.
        if alpha > 0:
            return (1.0 - alpha) * data_array[j - 1] + alpha * data_array[j]
    raise RuntimeError("something went wrong here...")


def eval_alpha(s, i, L):
    k = s * (L - 1)  # shifting percentage value to interval index.
    if i < k:
        alpha = 0.0
    elif k < i < k + 1:
        alpha = k - i + 1
    else:
        alpha = 1.0
    return alpha


def as_keyframe(orbit_center, orientation, distance):
    keyframe = {
        "OrbitCenter": Vec3(orbit_center),
        "Orientation": list(orientation),
        "Distance": distance,
    }
    return keyframe


def slerp(v0, v1, t_array):
    # interpolation between 2 quaternions (https://en.wikipedia.org/wiki/Slerp)
    # >>> slerp([1,0,0,0],[0,0,0,1],np.arange(0,1,0.001))
    # t_array = np.array(t_array)
    v0 = np.array(v0)
    v1 = np.array(v1)
    dot = np.sum(v0 * v1)

    if dot < 0.0:
        v1 = -v1
        dot = -dot

    DOT_THRESHOLD = 0.9995
    if dot > DOT_THRESHOLD:
        if isinstance(t_array, np.ndarray):
            result = (
                v0[np.newaxis, :] + t_array[:, np.newaxis] * (v1 - v0)[np.newaxis, :]
            )
        else:
            result = v0 + t_array * (v1 - v0)
        result = result / np.linalg.norm(result)
        return result

    theta_0 = np.arccos(dot)
    sin_theta_0 = np.sin(theta_0)

    theta = theta_0 * t_array
    sin_theta = np.sin(theta)

    s0 = np.cos(theta) - dot * sin_theta / sin_theta_0
    s1 = sin_theta / sin_theta_0

    if isinstance(t_array, np.ndarray):
        return (s0[:, np.newaxis] * v0[np.newaxis, :]) + (
            s1[:, np.newaxis] * v1[np.newaxis, :]
        )
    else:
        return s0 * v0 + s1 * v1


def quat_spline(q, s):
    # Implements a  spline interpolation (slerp) of N quaternions in spherical space of SO(3) (3-Sphere).
    # q is a vector of size 4 x N where N is the number unit quaternion vectors
    # s is a scalar from 0-1 that indicates where along the quaternion array the
    # interpolation is happening.
    # 'squad' :[s]pherical and [quad]rangle interpolation (see Ref[2] &
    # [3]). Analogous to bilinear interpolation in euclidean space.
    # squad is a sequence of  hierachical slerp interpolations.
    # squad(t,p,a,b,q) = slerp(2t(1-t),slerp(t,p,q),slerp(t,a,b));

    # Implmentation  based on the following papers.

    # [1] Kim, M. J., Kim, M. S., & Shin, S. Y. (1995, September). A general
    # construction scheme for unit quaternion curves with simple high order
    # derivatives. In Proceedings of the 22nd annual conference on Computer
    # graphics and interactive techniques (pp. 369-376). ACM.

    # Choice of end velocites isb ased on the following resources.
    # [2] Dam, Erik B., Martin Koch, and Martin Lillholm. Quaternions,
    # interpolation and animation. Datalogisk Institut, Københavns Universitet, 1998.
    # http://web.mit.edu/2.998/www/QuaternionReport1.pdf

    # [3] Eberly, David. "Quaternion algebra and calculus." Magic Software, Inc 21 (2002).
    # http://www.geometrictools.com/Documentation/Quaternions.pdf

    L = len(q)
    q = [np.array(qi) for qi in q]
    val = q[0]

    for j in range(1, L):
        C = np.dot(q[j - 1], q[j])
        if C < 0:
            q[j] = -q[j]

    C = np.dot(q[0], q[-1])

    if s == 0:  # saving calculation time -> where qm=qi
        return q[0]
    elif s == 1:  # saving calculation time -> where qm=qn
        return q[-1]

    for j in range(1, L):
        alpha = eval_alpha(
            s, j, L
        )  # shifting global percentage value to interval percentage.
        t = alpha

        if alpha > 0:
            EPS = 1e-9
            # Compute the cosine of the angle between the two vectors.
            C = np.dot(q[j - 1], q[j])
            if (
                1 - C
            ) <= EPS:  # if angle is close by epsilon to 0 degrees -> calculate by linear interpolation
                val = (
                    q[j - 1] * (1 - s) + q[j] * s
                )  # avoiding divisions by number close to 0
            elif (
                1 + C
            ) <= EPS:  # when teta is close by epsilon to 180 degrees the result is undefined -> no shortest direction to rotate
                # rotating one of the unit quaternions by 90 degrees -> q2
                qtemp = (q[j][3], -q[j][2], q[j][1], -q[j][0])
                qtemp_array = copy.deepcopy(q)
                qtemp_array[j] = qtemp

                qa = get_intermediate_control_point(j - 1, qtemp_array, 0)
                qap1 = get_intermediate_control_point(j, qtemp_array, 0)
                qtemp1 = slerp(q[j - 1], qtemp, t)
                qtemp2 = slerp(qa, qap1, t)
                squad = slerp(qtemp1, qtemp2, 2 * t * (1 - t))
                val = squad

            else:
                qa = get_intermediate_control_point(j - 1, q, 0)
                qap1 = get_intermediate_control_point(j, q, 0)
                qtemp1 = slerp(q[j - 1], q[j], t)
                qtemp2 = slerp(qa, qap1, t)
                squad = slerp(qtemp1, qtemp2, 2 * t * (1 - t))
                val = squad
            return quatnormalize(val)

    return quatnormalize(val)


def quatnormalize(q):
    """normalize a quaternion q, defined as a tuple or array of length 4"""
    return q / np.linalg.norm(np.array(q))


def quatinv(q):
    w0, x0, y0, z0 = q
    return np.array([w0, -x0, -y0, -z0]) / (np.linalg.norm(np.array(q)) ** 2)


def quatmultiply(quaternion1, quaternion0):
    w0, x0, y0, z0 = quaternion0
    w1, x1, y1, z1 = quaternion1
    return np.array(
        [
            -x1 * x0 - y1 * y0 - z1 * z0 + w1 * w0,
            x1 * w0 + y1 * z0 - z1 * y0 + w1 * x0,
            -x1 * z0 + y1 * w0 + z1 * x0 + w1 * y0,
            x1 * y0 - y1 * x0 + z1 * w0 + w1 * z0,
        ],
        dtype=np.float64,
    )


def quatlog(q):
    """natural logarithm of a quaternion (cf wikipedia)"""
    w0, x0, y0, z0 = q
    v = np.array([x0, y0, z0])
    q_norm = np.linalg.norm(np.array(q))
    fact = np.arccos(w0 / q_norm) / np.linalg.norm(v)
    return np.array([np.log(q_norm), fact * x0, fact * y0, fact * z0])


def quatexp(q):
    """exponential of a quaternion (cf wikipedia)"""
    w0, x0, y0, z0 = q
    v = np.array([x0, y0, z0])
    theta = np.linalg.norm(v)
    fact = np.sin(theta) / theta
    return np.exp(w0) * np.array(
        [np.cos(theta), fact * x0, fact * y0, fact * z0], dtype=np.float64
    )


def get_intermediate_control_point(j, q, dir_flip):
    # intermediate quaternions for spline continuity (the squad endpt conditions)
    # see page 54 of
    # Dam, Erik B., Martin Koch, and Martin Lillholm. Quaternions,
    # interpolation and animation. Datalogisk Institut, Københavns Universitet, 1998.
    # http://web.mit.edu/2.998/www/QuaternionReport1.pdf

    L = len(q)
    if j == 0:
        return q[0]
    elif j == L - 1:
        return q[-1]
    else:
        qji = quatinv(q[j])
        qiqm1 = quatmultiply(qji, q[j - 1])
        qiqp1 = quatmultiply(qji, q[j + 1])
        ang_vel = -((quatlog(qiqp1) + quatlog(qiqm1)) / 4)  # average of end pt tangents
        if dir_flip:
            qa = quatmultiply(q[j], quatinv(quatexp(ang_vel)))
        else:
            qa = quatmultiply(q[j], quatexp(ang_vel))
        qa = quatnormalize(qa)
    return qa
