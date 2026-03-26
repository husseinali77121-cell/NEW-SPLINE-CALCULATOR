import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

st.set_page_config(page_title="Spline Calculator - Biobase", layout="wide")
st.title("📊 حساب معاملات Spline لجهاز Biobase")
st.markdown("أدخل بيانات الامتصاصية مقابل التركيز، وسيقوم التطبيق بحساب معاملات شريحة المكعب الطبيعي (Natural Cubic Spline).")

# جلسة لحفظ البيانات المدخلة
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame({"Concentration": [], "Absorbance": []})

# عدد النقاط (ثابت: 4 أو 5)
col1, col2 = st.columns([1, 2])
with col1:
    n_points = st.selectbox("عدد النقاط:", [4, 5], index=0)
    st.write("أدخل القيم في الجدول أدناه:")

# إدخال البيانات عبر جدول تفاعلي
edited_df = st.data_editor(
    st.session_state.data,
    num_rows="dynamic",
    column_config={
        "Concentration": st.column_config.NumberColumn("التركيز", format="%.4f"),
        "Absorbance": st.column_config.NumberColumn("الامتصاصية", format="%.4f"),
    },
    use_container_width=True,
)

# تخزين البيانات في الجلسة
st.session_state.data = edited_df

# زر للحساب
if st.button("🔍 حساب المعاملات ورسم المنحنى", type="primary"):
    df = st.session_state.data.dropna()
    if len(df) < 2:
        st.error("الرجاء إدخال نقطتين على الأقل.")
    else:
        # ترتيب حسب التركيز
        df = df.sort_values("Concentration").reset_index(drop=True)
        x = df["Concentration"].values
        y = df["Absorbance"].values

        # التأكد من أن قيم التركيز فريدة (لـ spline)
        if len(np.unique(x)) != len(x):
            st.warning("يوجد تركيزات مكررة، سيتم التعامل معها ولكن النتائج قد لا تكون دقيقة.")

        # حساب Spline باستخدام scipy (طبيعي)
        try:
            cs = CubicSpline(x, y, bc_type='natural')
        except Exception as e:
            st.error(f"خطأ في الحساب: {e}")
            st.stop()

        # عرض المعاملات لكل فترة
        st.subheader("📈 معاملات Spline لكل فترة")
        intervals = []
        for i in range(len(x)-1):
            x_left = x[i]
            x_right = x[i+1]
            # نحصل على معاملات متعددة الحدود (تحتاج إلى استخراج المعاملات)
            # CubicSpline يوفر معاملات متعددة الحدود المحلية
            coeffs = cs.c[:, i]  # معاملات بالترتيب: c0, c1, c2, c3 (حسب الفترة)
            # المعادلة: S(x) = a + b*(x - x_left) + c*(x - x_left)^2 + d*(x - x_left)^3
            a = coeffs[0]
            b = coeffs[1]
            c = coeffs[2]
            d = coeffs[3]
            intervals.append({
                "الفترة": f"{x_left:.4f} → {x_right:.4f}",
                "Par A (a)": a,
                "Par B (b)": b,
                "Par C (c)": c,
                "Par D (d)": d,
            })
            st.write(f"**الفترة {i+1}:** من {x_left:.4f} إلى {x_right:.4f}")
            st.latex(f"S(x) = {a:.6f} + {b:.6f}(x-{x_left:.4f}) + {c:.6f}(x-{x_left:.4f})^2 + {d:.6f}(x-{x_left:.4f})^3")

        # عرض جدول المعاملات
        st.dataframe(pd.DataFrame(intervals), use_container_width=True)

        # رسم المنحنى
        st.subheader("📉 منحنى الانحدار (Spline)")
        x_smooth = np.linspace(x.min(), x.max(), 200)
        y_smooth = cs(x_smooth)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x_smooth, y_smooth, 'b-', label='Spline Interpolation', linewidth=2)
        ax.scatter(x, y, color='red', s=100, zorder=5, label='Data Points')
        ax.set_xlabel("Concentration", fontsize=12)
        ax.set_ylabel("Absorbance", fontsize=12)
        ax.set_title("Natural Cubic Spline", fontsize=14)
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig)

        # خيار التنبؤ لتركيز جديد
        st.subheader("🔮 توقع الامتصاصية لتركيز جديد")
        new_x = st.number_input("أدخل تركيزًا:", value=float(x.mean()), format="%.4f")
        if st.button("احسب الامتصاصية المتوقعة"):
            if new_x < x.min() or new_x > x.max():
                st.warning(f"التركيز خارج النطاق المدخل ({x.min():.4f} – {x.max():.4f}). سيتم استخدام أقرب فترة.")
            y_pred = cs(new_x)
            st.success(f"الامتصاصية المتوقعة عند التركيز **{new_x:.4f}** هي **{y_pred:.6f}**")