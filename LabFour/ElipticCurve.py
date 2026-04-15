class ElipticCurve:
    """
    a, b - коефіцієнти рівняння y² = x³ + ax + b
    p - просте число, модуль поля
    Ці три коефіцієнти однозначно задають еліптичну криву
    """
    def __init__(self, a, b, p ):
        self.a = a
        self.b = b
        self.p = p
        # Перевірка що крива несингулярна
        curve_discriminant = (4 * self.a**3 + 27 * self.b**2)% self.p 
        if curve_discriminant == 0:
            raise ValueError("Сингулярна крива: 4a³ + 27b² ≡ 0 (mod p)")
    
    def is_on_curve(self, x, y) -> bool:
        # Точка на нескінченності належить завжди
        if x is None and y is None:
            return True
        return (y**2) % self.p == ((x**3) + self.a * x + self.b) % self.p
    
    def simple_addition(self, x1, y1, x2, y2):
        """Simple means only 2 dots are supported
        Рівняння прямої: y = λ(x − x₁) + y₁
        Підставляємо це y в криву y² = x³ + ax + b:
        (λ(x − x₁) + y₁)² = x³ + ax + b
        """
        # (нуль групи + точка - просто повертаємо точку)
        if x1 is None:
            return x2, y2
        if x2 is None:
            return x1, y1
        
        # Протилежні точки (Вертикальна пряма ніколи не перетне третю точку, тому результат - нескінченність)
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None, None        
        
        if x1 == x2 and y1 == y2:
            # Подвоєння    
            interception_line_slope_coeff = ((3 * x1**2 + self.a) * pow(2 * y1, -1, self.p)) % self.p            
        else:    
            interception_line_slope_coeff = ((y2-y1) * pow(x2-x1, -1, self.p)) % self.p
            
        x3 = (interception_line_slope_coeff ** 2 - x1 - x2) % self.p
        y3 = (interception_line_slope_coeff*(x1-x3) - y1) % self.p
        return x3, y3
    
    def simple_scalar_multiplication(self, x1, y1, k):
        """Simple means greedy algorithm is used"""
        if k == 0:
            return None, None
        
        x_prev, y_prev = x1, y1
        for _ in range(k-1):
            x_prev, y_prev = self.simple_addition(x_prev, y_prev, x1, y1)
        return x_prev, y_prev

    def scalar_multiplication(self, x1, y1, k):
        """Double-and-add: O(log k) замість O(k)"""
        if k == 0:
            return None, None

        x_res, y_res = None, None
        for bit in bin(k)[2:]:
            x_res, y_res = self.simple_addition(x_res, y_res, x_res, y_res)
            if bit == '1':
                x_res, y_res = self.simple_addition(x_res, y_res, x1, y1)
        return x_res, y_res
