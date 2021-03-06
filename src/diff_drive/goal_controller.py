from __future__ import division, print_function
from math import pi, sqrt, sin, cos, atan2
from diff_drive.pose import Pose

class GoalController:
    """Finds linear and angular velocities necessary to drive toward
    a goal pose.
    """

    def __init__(self):
        self.kP = 3
        self.kA = 8
        self.kB = -1.5
        self.maxLinearSpeed = 1E9
        self.maxAngularSpeed = 1E9
        self.maxLinearAcceleration = 1E9
        self.linearTolerance = 0.025 # 2.5cm
        self.angularTolerance = 3/180*pi # 3 degrees
        self.forwardMovementOnly = False

    def setConstants(self, kP, kA, kB):
        self.kP = kP
        self.kA = kA
        self.kB = kB

    def setMaxLinearSpeed(self, speed):
        self.maxLinearSpeed = speed

    def setMaxAngularSpeed(self, speed):
        self.maxAngularSpeed = speed

    def setMaxLinearAcceleration(self, accel):
        self.maxLinearAcceleration = accel

    def setLinearTolerance(self, tolerance):
        self.linearTolerance = tolerance

    def setAngularTolerance(self, tolerance):
        self.angularTolerance = tolerance

    def setForwardMovementOnly(self, forwardOnly):
        self.forwardMovementOnly = forwardOnly

    def getGoalDistance(self, cur, goal):
        if goal is None:
            return 0
        diffX = cur.x - goal.x
        diffY = cur.y - goal.y
        return sqrt(diffX*diffX + diffY*diffY)

    def atGoal(self, cur, goal):
        if goal is None:
            return True
        d = self.getGoalDistance(cur, goal)
        dTh = abs(cur.theta - goal.theta)
        return d < self.linearTolerance and dTh < self.angularTolerance

    def getVelocity(self, cur, goal, dT):
        desired = Pose()

        a = -cur.theta + atan2(goal.y - cur.y, goal.x - cur.x)

        # In Automomous Mobile Robots, they assume theta_G=0. So for
        # the error in heading, we have to adjust theta based on the
        # (possibly non-zero) goal theta.
        theta = cur.theta - goal.theta
        b = -theta - a

        d = self.getGoalDistance(cur, goal)
        if self.forwardMovementOnly:
            direction = 1
            a = self.normalizePi(a)
            b = self.normalizePi(b)
            #if abs(a) > pi/2:
            #    b = 0
        else:
            direction = self.sign(cos(a))
            a = self.normalizeHalfPi(a)
            b = self.normalizeHalfPi(b)

        if abs(d) < self.linearTolerance:
            desired.xVel = 0
            desired.thetaVel = self.kB * theta
        else:
            desired.xVel = self.kP * d * direction
            desired.thetaVel = self.kA*a + self.kB*b

        #print('current x:', cur.x, 'y:', cur.y, 'theta:', cur.theta,
        #    '  goal x:', goal.x, 'y:', goal.y, 'theta:', goal.theta)
        #print('  theta:', theta, 'a:', a, 'b:', b,
        #    'v:', desired.xVel, 'w:', desired.thetaVel)
        #print(str(cur.x) + ',' + str(cur.y) + ',' + str(cur.theta))

        # TBD: Adjust velocities if linear or angular rates
        # or acceleration too high.

        return desired

    def normalizeHalfPi(self, alpha):
        if alpha > pi/2:
            return alpha - pi
        elif alpha < -pi/2:
            return alpha + pi
        else:
            return alpha

    def normalizePi(self, alpha):
        if alpha > pi:
            return alpha - 2*pi
        elif alpha < -pi:
            return alpha + 2*pi
        else:
            return alpha

    def sign(self, x):
        if x >= 0:
            return 1
        else:
            return -1
