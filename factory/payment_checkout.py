#!/usr/bin/env python3
"""
AI24x7 Factory Edition - Stripe Payment Page
Generates checkout links for factory plans
Run: streamlit run payment_checkout.py --server.port 5055
"""
import streamlit as st
import urllib.parse

st.set_page_config(page_title="AI24x7 Factory - Buy", page_icon="🏭", layout="centered")

st.markdown("""
<style>
    .stApp { background: #0e1117; }
    .plan-card { background: #1a1f2e; border-radius: 16px; padding: 24px; margin: 8px; border: 2px solid #2a3441; text-align: center; }
    .plan-card:hover { border-color: #00d4aa; }
    .plan-selected { border-color: #00d4aa; background: #0f2922; }
    .price { font-size: 2.5rem; font-weight: bold; color: #00d4aa; }
    .price-small { font-size: 1rem; color: #8b95a5; }
    .feature-item { padding: 6px 0; border-bottom: 1px solid #1e2533; }
    .cta-button { background: linear-gradient(135deg, #00d4aa, #00a866); color: white; padding: 14px 32px; border-radius: 12px; font-size: 1.1rem; font-weight: bold; border: none; cursor: pointer; width: 100%; }
    .cta-button:hover { opacity: 0.9; }
    .badge { background: #ff4444; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .best-badge { background: linear-gradient(135deg, #ffaa00, #ff6600); color: white; padding: 4px 14px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1>🏭 AI24x7 Factory Edition</h1>
    <p style="color: #8b95a5; font-size: 1.1rem;">Industrial AI Surveillance — Hindi + English Voice Alerts</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Stripe test mode notice
st.warning("🔒 Test Mode: Use card `4242 4242 4242 4242` for testing. No real charges.")

# Plan definitions
PLANS = {
    "factory_lite": {
        "name": "Factory Lite",
        "price": 2999,
        "badge": "",
        "description": "Perfect for small factories",
        "features": [
            "📹 4 CCTV Cameras",
            "🔥 Fire Detection (AI)",
            "🪖 PPE Detection (Helmet/Vest)",
            "📊 Daily Shift Reports",
            "📱 Telegram Alerts",
            "💬 Hindi + English TTS",
            "🖥️ Local Dashboard",
            "⚡ GPU-Powered AI",
        ],
        "stripe_price_id": "price_test_factory_lite",  # Replace with real Stripe Price ID
    },
    "factory_pro": {
        "name": "Factory Pro",
        "badge": "⭐ BEST VALUE",
        "description": "Complete safety suite",
        "price": 9999,
        "features": [
            "📹 16 CCTV Cameras",
            "🔥 Fire Detection (AI)",
            "🪖 PPE Detection (AI)",
            "🚨 Fall Detection",
            "🛢️ Spill/Hazard Detection",
            "🚗 ANPR Vehicle Access",
            "⚙️ Equipment Monitor",
            "📋 Shift Reports",
            "📱 Telegram + SMS + WhatsApp",
            "🔊 Voice Announcements",
            "💬 Hindi + English TTS",
            "🖥️ Professional Dashboard",
        ],
        "stripe_price_id": "price_test_factory_pro",
    },
    "factory_enterprise": {
        "name": "Factory Enterprise",
        "badge": "🏢 ENTERPRISE",
        "description": "Multi-site, unlimited",
        "price": 24999,
        "features": [
            "📹 Unlimited Cameras",
            "🔥 Fire Detection (AI)",
            "🪖 PPE Detection (AI)",
            "🚨 Fall Detection",
            "🛢️ Spill/Hazard Detection",
            "🚗 ANPR Vehicle Access",
            "⚙️ Equipment Monitor",
            "📋 Shift Reports",
            "📱 All Alert Channels",
            "🔊 Voice Announcements",
            "🏭 Multi-Site Management",
            "🎨 White Label Ready",
            "🔄 Auto Updates",
            "🎯 Priority Support",
        ],
        "stripe_price_id": "price_test_factory_enterprise",
    },
}

# Plan selection
cols = st.columns(3)
selected_plan = None

for idx, (plan_key, plan) in enumerate(PLANS.items()):
    with cols[idx]:
        badge_html = f'<span class="best-badge">{plan["badge"]}</span>' if plan["badge"] else ""
        st.markdown(f"""
        <div class="plan-card">
            {badge_html}
            <h2 style="color: white; margin-top: 10px;">{plan["name"]}</h2>
            <p style="color: #8b95a5; font-size: 0.85rem;">{plan["description"]}</p>
            <div class="price">₹{plan["price"]:,}<span class="price-small">/month</span></div>
            <hr style="border-color: #2a3441;">
        """, unsafe_allow_html=True)
        
        for feature in plan["features"]:
            st.markdown(f'<div class="feature-item" style="color: #c8d0dc; font-size: 0.88rem;">{feature}</div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button(f"Buy {plan['name']}", key=f"buy_{plan_key}", use_container_width=True):
            selected_plan = plan_key

st.markdown("---")

# Checkout form
if selected_plan:
    plan = PLANS[selected_plan]
    st.markdown(f"## 🛒 Checkout: {plan['name']}")
    
    with st.form("checkout_form"):
        st.markdown("**Your Details**")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="Ramesh Kumar")
            email = st.text_input("Email", placeholder="ramesh@factory.com")
        with col2:
            phone = st.text_input("WhatsApp Number", placeholder="+91-9876543210")
            factory_name = st.text_input("Factory Name", placeholder="Alpha Industries")
        
        camera_count = st.slider("Number of Cameras", 2, 100, 16 if selected_plan == "factory_pro" else 4 if selected_plan == "factory_lite" else 50)
        
        st.markdown(f"**Plan:** {plan['name']} — ₹{plan['price']:,}/month")
        st.markdown(f"**Cameras:** {camera_count}")
        st.markdown(f"**Total:** ₹{plan['price']:,}/month (billed monthly)")
        
        submitted = st.form_submit_button("💳 Proceed to Payment (Stripe)", use_container_width=True)
        
        if submitted:
            if not name or not email:
                st.error("Please fill all required fields")
            else:
                # Generate Stripe Checkout session URL
                # In production, replace with actual Stripe API call
                st.info("🔒 Redirecting to Stripe Checkout...")
                
                # Demo: show the link that would be generated
                params = urllib.parse.urlencode({
                    "plan": selected_plan,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "factory": factory_name,
                    "cameras": camera_count,
                })
                
                st.success(f"""
                **✅ Demo Mode** 
                
                In production, this would create a Stripe Checkout session:
                
                ```
                POST /create-checkout-session
                → Redirect to: https://checkout.stripe.com/...
                
                Plan: {plan['name']}
                Amount: ₹{plan['price']:,}
                Customer: {name} <{email}>
                Factory: {factory_name}
                ```
                
                **Stripe Test Card:** `4242 4242 4242 4242`
                """)
                
                # Real Stripe implementation:
                # import stripe
                # stripe.api_key = "sk_test_..."
                # session = stripe.checkout.Session.create(
                #     payment_method_types=['card'],
                #     line_items=[{
                #         'price_data': {
                #             'currency': 'inr',
                #             'product_data': {'name': f'AI24x7 {plan["name"]}'},
                #             'unit_amount': plan['price'] * 100,
                #         },
                #         'quantity': 1,
                #     }],
                #     mode='subscription',
                #     success_url='https://ai24x7.com/success?session_id={CHECKOUT_SESSION_ID}',
                #     cancel_url='https://ai24x7.com/cancel',
                #     customer_email=email,
                #     metadata={'plan': selected_plan, 'name': name}
                # )
                # st.markdown(f"[Pay Now]({session.url})")

else:
    st.markdown("""
    <div style="text-align: center; padding: 30px; color: #8b95a5;">
        <h3>All plans include:</h3>
        <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; margin-top: 15px;">
            <span>✅ 24/7 AI Monitoring</span>
            <span>✅ Hindi Voice Alerts</span>
            <span>✅ Telegram Integration</span>
            <span>✅ GPU Acceleration</span>
            <span>✅ License Protection</span>
            <span>✅ Auto Updates</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #4a5568; font-size: 0.8rem; padding: 20px;">
    🔒 Payments secured by Stripe | AI24x7 © 2026 GOUP CONSULTANCY SERVICES LLP<br>
    Contact: arjun@goup.co.in | WhatsApp: +91-98765-XXXXX
</div>
""", unsafe_allow_html=True)
