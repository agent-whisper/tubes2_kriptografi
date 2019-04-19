class EllipticCurveOp():
    @staticmethod
    def sum_point(point_a, point_b, elliptic_curve) :
        if (point_a.x == point_b.x and point_a.y == point_b.y) :
            m = ((3*(point_a.x**2) + elliptic_curve.a) \
                * pow(2 * point_a.y,elliptic_curve.p-2,elliptic_curve.p)) \
                    % elliptic_curve.p
            xr = ((m ** 2) - 2*point_a.x) % elliptic_curve.p
            yr = (m * (point_a.x - xr) - point_a.y) % elliptic_curve.p
        else :
            m = ((point_a.y - point_b.y) \
                * pow(point_a.x-point_b.x,elliptic_curve.p-2,elliptic_curve.p)) \
                    % elliptic_curve.p
            xr = ((m ** 2) - point_a.x - point_b.x) % elliptic_curve.p
            yr = (m * (point_a.x - xr) - point_a.y) % elliptic_curve.p
        return Point(xr, yr)

    @staticmethod
    def multiply_point(k, point, elliptic_curve) :
        current_point = point
        for i in range(1, k) :
            current_point = EllipticCurveOp.sum_point(point, current_point, elliptic_curve)
        return current_point

    @staticmethod
    def subs_point(point_a, point_b, elliptic_curve) :
        point_b = Point(point_b.x, (point_b.y * -1) % elliptic_curve.p)
        return (EllipticCurveOp.sum_point(point_a, point_b, elliptic_curve))

class EllipticCurve():
    def __init__(self, coefficient, constant, prime_num, equation, order = None):
        self.a = coefficient
        self.b = constant
        self.p = prime_num
        self.E = equation
        self.order = order

    def contains_point(self, P):
        return (self.E(P.x) % self.p) == (P.y**2 % self.p)

    def generate_base_point(self) :
        found = False
        base = (0,0)
        for x in range (0, self.p) :
            for y in range (0, self.p) :
                if ((self.E(x) % self.p) == (y**2 % self.p)) :
                    base = Point(x, y)
                    found = True
                    break
            if (found):
                break
        return base

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '(%d, %d)' % (self.x, self.y)