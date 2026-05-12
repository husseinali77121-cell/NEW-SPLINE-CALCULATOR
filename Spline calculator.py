import numpy as np

def natural_cubic_spline(x, y):
    """
    حساب معاملات Natural Cubic Spline.
    
    المعاملات لكل فترة i:
        S_i(x) = A_i + B_i*(x - x_i) + C_i*(x - x_i)^2 + D_i*(x - x_i)^3
    حيث:
        A_i = y_i
        B_i = معامل الخطي
        C_i = معامل التربيعي
        D_i = معامل التكعيبي
    
    المدخلات:
        x: قائمة تركيزات (يجب أن تكون متزايدة)
        y: قائمة امتصاصية مقابلة
    
    المخرجات:
        list of tuples: (A, B, C, D) لكل فترة
    """
    n = len(x) - 1  # عدد الفترات
    h = [x[i+1] - x[i] for i in range(n)]
    
    # بناء المصفوفة الثلاثية القطرية
    A_matrix = np.zeros((n+1, n+1))
    b = np.zeros(n+1)
    
    # الحدود الطبيعية (second derivatives = 0 عند الأطراف)
    A_matrix[0][0] = 1.0
    A_matrix[n][n] = 1.0
    
    for i in range(1, n):
        A_matrix[i][i-1] = h[i-1]
        A_matrix[i][i] = 2 * (h[i-1] + h[i])
        A_matrix[i][i+1] = h[i]
        b[i] = 3 * ((y[i+1] - y[i]) / h[i] - (y[i] - y[i-1]) / h[i-1])
    
    # حل النظام لإيجاد المشتقات الثانية
    c = np.linalg.solve(A_matrix, b)  # c[i] = S''(x_i)/2
    
    # حساب المعاملات لكل فترة
    coeffs = []
    for i in range(n):
        A = y[i]
        B = (y[i+1] - y[i]) / h[i] - h[i] * (2*c[i] + c[i+1]) / 3
        C = c[i]
        D = (c[i+1] - c[i]) / (3 * h[i])
        coeffs.append((A, B, C, D))
    
    return coeffs

def main():
    print("برنامج حساب معاملات Spline من بيانات الامتصاصية والتركيز")
    print("="*60)
    
    # إدخال عدد النقاط
    while True:
        try:
            n = int(input("أدخل عدد النقاط (4 أو 5 مثلاً): "))
            if n >= 2:
                break
            else:
                print("يجب أن يكون العدد 2 على الأقل.")
        except ValueError:
            print("الرجاء إدخال رقم صحيح.")
    
    # إدخال البيانات
    concentrations = []
    absorbances = []
    
    print("\nأدخل البيانات (التركيز أولاً ثم الامتصاصية):")
    for i in range(n):
        print(f"\nالنقطة {i+1}:")
        while True:
            try:
                c = float(input("  التركيز (Concentration): "))
                a = float(input("  الامتصاصية (Absorbance): "))
                concentrations.append(c)
                absorbances.append(a)
                break
            except ValueError:
                print("الرجاء إدخال أرقام صحيحة.")
    
    # التأكد من ترتيب التركيزات تصاعدياً (إذا لم تكن مرتبة يمكن فرزها)
    if not all(concentrations[i] <= concentrations[i+1] for i in range(n-1)):
        print("\nتم فرز البيانات حسب التركيز.")
        combined = sorted(zip(concentrations, absorbances))
        concentrations, absorbances = zip(*combined)
        concentrations = list(concentrations)
        absorbances = list(absorbances)
    
    # حساب المعاملات
    coeffs = natural_cubic_spline(concentrations, absorbances)
    
    # عرض النتائج
    print("\n" + "="*60)
    print("معاملات Spline لكل فترة:")
    print("-"*60)
    for i, (A, B, C, D) in enumerate(coeffs):
        print(f"\nالفترة {i+1}: من x = {concentrations[i]:.4f} إلى x = {concentrations[i+1]:.4f}")
        print(f"  Par A (a_i) = {A:.6f}")
        print(f"  Par B (b_i) = {B:.6f}")
        print(f"  Par C (c_i) = {C:.6f}")
        print(f"  Par D (d_i) = {D:.6f}")
        print(f"  المعادلة: S(x) = {A:.6f} + {B:.6f}*(x - {concentrations[i]:.4f}) + {C:.6f}*(x - {concentrations[i]:.4f})^2 + {D:.6f}*(x - {concentrations[i]:.4f})^3")
    
    # خيار إضافي: إدخال تركيز للتنبؤ بالامتصاصية
    print("\n" + "="*60)
    try:
        x_pred = float(input("أدخل تركيزًا للتنبؤ بالامتصاصية (أو اضغط Enter لتخطي): ") or "skip")
        if x_pred != "skip":
            # تحديد الفترة المناسبة
            if x_pred < concentrations[0] or x_pred > concentrations[-1]:
                print("التركيز خارج النطاق المدخل. سيتم استخدام أقرب فترة.")
                if x_pred < concentrations[0]:
                    i = 0
                else:
                    i = len(coeffs)-1
            else:
                for i in range(len(coeffs)):
                    if concentrations[i] <= x_pred <= concentrations[i+1]:
                        break
            A, B, C, D = coeffs[i]
            dx = x_pred - concentrations[i]
            y_pred = A + B*dx + C*dx**2 + D*dx**3
            print(f"الامتصاصية المتوقعة عند التركيز {x_pred:.4f} هي {y_pred:.6f}")
    except:
        pass

if __name__ == "__main__":
    main()
