"""
Demo UI con Streamlit - Validación E2E del sistema
Permite probar manualmente el flujo completo de detección de fraude

Nota:
Esta demo sirve para validación BDD y demostración, no es la UI final.
La IA sugirió hacer una UI compleja. La simplifiqué a lo esencial para MVP.
"""
import streamlit as st
import requests
from datetime import datetime
import os

# Configuración
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Fraud Detection Engine - Demo", page_icon="🛡️", layout="wide"
)

st.title("🛡️ Fraud Detection Engine - Demo")
st.markdown("Motor de detección de fraude con Clean Architecture y SOLID")

# Tabs para diferentes funcionalidades
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📝 Evaluar Transacción", "👤 Transacciones por Usuario", "📊 Auditoría", "👨‍💼 Revisión Manual", "⚙️ Configuración"]
)

# Tab 1: Evaluar Transacción
with tab1:
    st.header("Evaluar Nueva Transacción")

    with st.form("transaction_form"):
        col1, col2 = st.columns(2)

        with col1:
            txn_id = st.text_input("Transaction ID", value=f"txn_{datetime.now().strftime('%Y%m%d%H%M%S')}")
            amount = st.number_input("Monto (USD)", min_value=0.01, value=1200.00, step=100.00)
            user_id = st.text_input("User ID", value="user_123")

        with col2:
            latitude = st.number_input(
                "Latitud", min_value=-90.0, max_value=90.0, value=40.7128, step=0.0001
            )
            longitude = st.number_input(
                "Longitud", min_value=-180.0, max_value=180.0, value=-74.0060, step=0.0001
            )

        submit_btn = st.form_submit_button("🚀 Evaluar Transacción", use_container_width=True)

        if submit_btn:
            payload = {
                "id": txn_id,
                "amount": amount,
                "user_id": user_id,
                "location": {"latitude": latitude, "longitude": longitude},
                "timestamp": datetime.now().isoformat(),
            }

            try:
                response = requests.post(f"{API_URL}/transaction", json=payload, timeout=5)

                if response.status_code == 202:
                    data = response.json()
                    risk_level = data.get("risk_level", "UNKNOWN")

                    if risk_level == "HIGH_RISK":
                        st.error(f"⚠️ **ALTO RIESGO DETECTADO**")
                    elif risk_level == "MEDIUM_RISK":
                        st.warning(f"⚡ **RIESGO MEDIO DETECTADO**")
                    else:
                        st.success(f"✅ **BAJO RIESGO - APROBADO**")

                    st.json(data)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

            except requests.ConnectionError:
                st.error("❌ No se puede conectar a la API. ¿Está corriendo el servidor?")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Tab 2: Transacciones por Usuario
with tab2:
    st.header("👤 Transacciones por Usuario")
    st.markdown("Visualiza todas las transacciones realizadas por un usuario específico")

    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_user_id = st.text_input("🔍 User ID", placeholder="Ej: user_123", key="search_user")
    
    with col2:
        st.write("")  # Espaciador
        st.write("")  # Espaciador
        search_btn = st.button("🔎 Buscar", use_container_width=True)

    if search_btn and search_user_id:
        try:
            with st.spinner(f"Buscando transacciones de {search_user_id}..."):
                response = requests.get(f"{API_URL}/audit/user/{search_user_id}", timeout=5)

                if response.status_code == 200:
                    transactions = response.json()

                    if not transactions:
                        st.info(f"📭 No se encontraron transacciones para el usuario {search_user_id}")
                    else:
                        st.success(f"✅ Se encontraron {len(transactions)} transacciones")
                        
                        # Estadísticas del usuario
                        col1, col2, col3, col4 = st.columns(4)
                        
                        high_risk_count = sum(1 for t in transactions if t["risk_level"] == "HIGH_RISK")
                        medium_risk_count = sum(1 for t in transactions if t["risk_level"] == "MEDIUM_RISK")
                        low_risk_count = sum(1 for t in transactions if t["risk_level"] == "LOW_RISK")
                        approved_count = sum(1 for t in transactions if t["status"] == "APPROVED")
                        
                        with col1:
                            st.metric("🔴 Alto Riesgo", high_risk_count)
                        with col2:
                            st.metric("🟡 Riesgo Medio", medium_risk_count)
                        with col3:
                            st.metric("🟢 Bajo Riesgo", low_risk_count)
                        with col4:
                            st.metric("✅ Aprobadas", approved_count)
                        
                        st.divider()
                        
                        # Tabla de transacciones
                        st.subheader("📋 Historial de Transacciones")
                        
                        for idx, txn in enumerate(transactions, 1):
                            risk_color = {
                                "HIGH_RISK": "🔴",
                                "MEDIUM_RISK": "🟡",
                                "LOW_RISK": "🟢",
                            }.get(txn["risk_level"], "⚪")
                            
                            status_icon = "✅" if txn["status"] == "APPROVED" else "⏳" if txn["status"] == "PENDING_REVIEW" else "❌"
                            
                            with st.expander(
                                f"{idx}. {risk_color} {txn['transaction_id']} - {txn['risk_level']} {status_icon}",
                                expanded=(idx <= 3)  # Expandir las primeras 3
                            ):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write(f"**Transaction ID:** {txn['transaction_id']}")
                                    st.write(f"**User ID:** {txn['user_id']}")
                                    st.write(f"**Nivel de Riesgo:** {risk_color} {txn['risk_level']}")
                                    st.write(f"**Score de Riesgo:** {txn.get('risk_score', 'N/A')}")
                                
                                with col2:
                                    st.write(f"**Estado:** {status_icon} {txn['status']}")
                                    st.write(f"**Evaluado:** {txn['evaluated_at']}")
                                    if txn.get('reviewed_by'):
                                        st.write(f"**Revisado por:** {txn['reviewed_by']}")
                                        st.write(f"**Revisado en:** {txn.get('reviewed_at', 'N/A')}")
                                
                                if txn.get('reasons'):
                                    st.write("**Razones:**")
                                    for reason in txn['reasons']:
                                        st.write(f"- {reason}")
                                
                                # Botón para ver detalles JSON
                                if st.button(f"Ver JSON completo", key=f"json_{txn['transaction_id']}"):
                                    st.json(txn)
                
                elif response.status_code == 404:
                    st.warning(f"⚠️ No se encontraron transacciones para el usuario {search_user_id}")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

        except requests.ConnectionError:
            st.error("❌ No se puede conectar a la API. ¿Está corriendo el servidor?")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    elif search_btn and not search_user_id:
        st.warning("⚠️ Por favor ingresa un User ID para buscar")

# Tab 3: Auditoría
with tab3:
    st.header("Auditoría de Evaluaciones")

    if st.button("🔄 Cargar Evaluaciones", use_container_width=True):
        try:
            response = requests.get(f"{API_URL}/audit/all", timeout=5)

            if response.status_code == 200:
                evaluations = response.json()

                if not evaluations:
                    st.info("No hay evaluaciones registradas")
                else:
                    st.success(f"✅ {len(evaluations)} evaluaciones encontradas")

                    for eval_data in evaluations:
                        risk_color = {
                            "HIGH_RISK": "🔴",
                            "MEDIUM_RISK": "🟡",
                            "LOW_RISK": "🟢",
                        }.get(eval_data["risk_level"], "⚪")

                        with st.expander(
                            f"{risk_color} {eval_data['transaction_id']} - {eval_data['risk_level']} - {eval_data['status']}"
                        ):
                            st.json(eval_data)
            else:
                st.error(f"Error {response.status_code}: {response.text}")

        except requests.ConnectionError:
            st.error("❌ No se puede conectar a la API")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Tab 4: Revisión Manual
with tab4:
    st.header("Revisión Manual (Human in the Loop)")

    col1, col2 = st.columns([2, 1])

    with col1:
        review_txn_id = st.text_input("Transaction ID a revisar", key="review_id")
    with col2:
        decision = st.selectbox("Decisión", ["APPROVED", "REJECTED"])

    analyst_id = st.text_input("Analyst ID", value="analyst_demo")

    if st.button("✍️ Enviar Revisión", use_container_width=True):
        if not review_txn_id:
            st.warning("Por favor ingrese un Transaction ID")
        elif not analyst_id:
            st.warning("Por favor ingrese un Analyst ID")
        else:
            try:
                response = requests.put(
                    f"{API_URL}/transaction/review/{review_txn_id}",
                    json={"decision": decision},
                    headers={"X-Analyst-ID": analyst_id},
                    timeout=5,
                )

                if response.status_code == 200:
                    st.success(f"✅ Revisión aplicada: {decision}")
                    st.json(response.json())
                elif response.status_code == 404:
                    st.error("❌ Transacción no encontrada")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

            except requests.ConnectionError:
                st.error("❌ No se puede conectar a la API")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Tab 5: Configuración
with tab5:
    st.header("Configuración de Umbrales (Sin Redespliegue)")

    # Cargar configuración actual
    if st.button("📥 Cargar Configuración Actual"):
        try:
            response = requests.get(f"{API_URL}/config/thresholds", timeout=5)
            if response.status_code == 200:
                config = response.json()
                st.success("✅ Configuración cargada")
                st.json(config)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    st.divider()

    # Actualizar configuración
    with st.form("config_form"):
        new_amount_threshold = st.number_input(
            "Nuevo Umbral de Monto (USD)", min_value=0.01, value=1500.00, step=100.00
        )
        new_location_radius = st.number_input(
            "Nuevo Radio de Ubicación (km)", min_value=1.0, value=100.0, step=10.0
        )
        config_analyst_id = st.text_input("Analyst ID", value="analyst_config")

        submit_config = st.form_submit_button("💾 Actualizar Configuración")

        if submit_config:
            if not config_analyst_id:
                st.warning("Por favor ingrese un Analyst ID")
            else:
                try:
                    response = requests.put(
                        f"{API_URL}/config/thresholds",
                        json={
                            "amount_threshold": new_amount_threshold,
                            "location_radius_km": new_location_radius,
                        },
                        headers={"X-Analyst-ID": config_analyst_id},
                        timeout=5,
                    )

                    if response.status_code == 200:
                        st.success("✅ Configuración actualizada exitosamente")
                        st.json(response.json())
                        st.info(
                            "ℹ️ Los nuevos umbrales se aplicarán en las siguientes evaluaciones"
                        )
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Footer
st.divider()
st.markdown(
    """
    **Fraud Detection Engine v0.1.0**  
    Desarrollado con Clean Architecture + SOLID + TDD/BDD  
    [GitHub](https://github.com) | [Documentación](README.md)
    """
)
