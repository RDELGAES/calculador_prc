# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import math

# Configuração inicial da página (deve ser a primeira instrução)
st.set_page_config(page_title="Calculadora PRC", layout="centered")

# ===========================================
# Injeção de CSS para posicionar o botão de idioma no canto superior direito
# ===========================================
st.markdown(
    """
    <style>
    .fixed-lang-button {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 100;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===========================================
# Dicionários de Tradução
# ===========================================
translations = {
    "Português": {
        "title": "Calculadora de Custos – PRC vs. RTS Tradicional",
        "description": (
            "Esta calculadora reflete o racional do seu simulador:\n\n"
            "- **Com PRC**:\n"
            "  - Até 50 USD: 20% de Imp. de Importação + ICMS 17% por dentro.\n"
            "  - Acima de 50 USD: 60% de Imp. de Importação, com desconto fixo de 20 USD, + ICMS 17% por dentro.\n"
            "- **Sem PRC (RTS Tradicional)**:\n"
            "  - 60% de Imp. de Importação + ICMS 17% por dentro."
        ),
        "dolar_label": "Cotação do Dólar (USD → BRL)",
        "auto_cotacao": "Atualizar cotação via API (PTAX)",
        "remessa": "Dados da Remessa",
        "product": "Valor do Produto (USD):",
        "freight": "Frete Internacional (USD):",
        "insurance": "Seguro (USD):",
        "last_mile": "Last Mile (USD):",
        "other_expenses": "Outras Despesas (USD):",
        "volume": "Volume de Remessas Projetadas por Ano:",
        "regime": "Selecione o Regime",
        "prc": "Sim (PRC)",
        "rts": "Não (RTS Tradicional)",
        "resultado": "Resultado da Simulação (Por Remessa)",
        "imp": "Imposto de Importação",
        "icms": "ICMS",
        "total": "Total a Pagar",
        "anual": "Projeção Anual",
        "custo_anual": "Custo Anual Total",
        "comparacao": "Comparação com o Outro Regime",
        "economia": "Usando PRC, você economiza {usd} USD (R$ {brl}) por ano em comparação com o regime RTS Tradicional.",
        "troca": "Se você adotasse o PRC, economizaria {usd} USD (R$ {brl}) por ano.",
        "export": "Exportar Resultado",
        "baixar_csv": "Baixar CSV",
        "error_cotacao": "Não foi possível buscar a cotação PTAX automaticamente. Verifique sua conexão ou use a cotação manual."
    },
    "English": {
        "title": "Cost Calculator – PRC vs. Traditional RTS",
        "description": (
            "This calculator reflects the rationale of your simulator:\n\n"
            "- **With PRC**:\n"
            "  - Up to 50 USD: 20% Import Tax + 17% ICMS calculated cumulatively.\n"
            "  - Above 50 USD: 60% Import Tax with a fixed discount of 20 USD, plus 17% ICMS cumulatively.\n"
            "- **Without PRC (Traditional RTS)**:\n"
            "  - 60% Import Tax + 17% ICMS calculated cumulatively."
        ),
        "dolar_label": "Dollar Exchange Rate (USD → BRL)",
        "auto_cotacao": "Update exchange rate via API (PTAX)",
        "remessa": "Shipment Data",
        "product": "Product Value (USD):",
        "freight": "International Freight (USD):",
        "insurance": "Insurance (USD):",
        "last_mile": "Last Mile (USD):",
        "other_expenses": "Other Expenses (USD):",
        "volume": "Projected Number of Shipments per Year:",
        "regime": "Select the Regime",
        "prc": "Yes (PRC)",
        "rts": "No (Traditional RTS)",
        "resultado": "Simulation Result (Per Shipment)",
        "imp": "Import Tax",
        "icms": "ICMS",
        "total": "Total to Pay",
        "anual": "Annual Projection",
        "custo_anual": "Total Annual Cost",
        "comparacao": "Comparison with the Other Regime",
        "economia": "By using PRC, you save {usd} USD (R$ {brl}) per year compared to the Traditional RTS regime.",
        "troca": "Switching to PRC, you could save {usd} USD (R$ {brl}) per year.",
        "export": "Export Result",
        "baixar_csv": "Download CSV",
        "error_cotacao": "Could not fetch the PTAX exchange rate automatically. Please check your connection or enter the rate manually."
    },
    "中文": {
        "title": "成本计算器 – PRC vs. 传统RTS",
        "description": (
            "该计算器反映了您的模拟器逻辑：\n\n"
            "- **使用PRC**：\n"
            "  - 低于50美元：20%进口税 + 17% ICMS（累进计算）。\n"
            "  - 超过50美元：60%进口税，减去20美元固定折扣，再加17% ICMS（累进计算）。\n"
            "- **不使用PRC（传统RTS）**：\n"
            "  - 60%进口税 + 17% ICMS（累进计算）。"
        ),
        "dolar_label": "美元汇率 (USD → BRL)",
        "auto_cotacao": "通过 API (PTAX) 更新汇率",
        "remessa": "货件数据",
        "product": "产品价值 (USD):",
        "freight": "国际运费 (USD):",
        "insurance": "保险 (USD):",
        "last_mile": "最后一英里 (USD):",
        "other_expenses": "其他费用 (USD):",
        "volume": "每年预计货件数量:",
        "regime": "选择计税方式",
        "prc": "是 (PRC)",
        "rts": "否 (传统RTS)",
        "resultado": "单笔货件计算结果",
        "imp": "进口税",
        "icms": "ICMS",
        "total": "应付总额",
        "anual": "年度预测",
        "custo_anual": "年度总成本",
        "comparacao": "与另一计税方式的比较",
        "economia": "使用PRC，每年可比传统RTS节省 {usd} 美元 (R$ {brl})。",
        "troca": "切换到PRC，每年可节省 {usd} 美元 (R$ {brl})。",
        "export": "导出结果",
        "baixar_csv": "下载 CSV",
        "error_cotacao": "无法自动获取 PTAX 汇率。请检查您的网络或手动输入汇率。"
    }
}

# ===========================================
# Funções para Formatação de Números e Moedas
# ===========================================
def format_number(value, lang):
    if lang == "Português":
        formatted = f"{value:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        formatted = f"{value:,.2f}"
    return formatted

def format_currency(value, currency, lang):
    formatted = format_number(value, lang)
    return f"{currency} {formatted}"

def format_rate(value, lang):
    # Exibe a taxa com 4 dígitos decimais sem arredondamento.
    formatted = f"{value:.4f}"
    if lang == "Português":
        formatted = formatted.replace(".", ",")
    return formatted

# ===========================================
# Função para truncar um número sem arredondar
# ===========================================
def truncate(f, n=4):
    factor = 10 ** n
    return math.floor(f * factor) / factor

# ===========================================
# Funções de Cálculo
# ===========================================
def calc_icms_por_dentro(base, import_tax, icms_rate=0.17):
    x = icms_rate * (base + import_tax)
    icms = x / (1 - icms_rate)
    return icms

def calc_prc(base):
    if base < 50:
        import_tax_bruto = 0.20 * base
        icms = calc_icms_por_dentro(base, import_tax_bruto)
        total = base + import_tax_bruto + icms
        return import_tax_bruto, icms, total
    else:
        import_tax_bruto = 0.60 * base
        import_tax_final = max(import_tax_bruto - 20, 0)
        icms = calc_icms_por_dentro(base, import_tax_final)
        total = base + import_tax_final + icms
        return import_tax_final, icms, total

def calc_no_prc(base):
    import_tax = 0.60 * base
    icms = calc_icms_por_dentro(base, import_tax)
    total = base + import_tax + icms
    return import_tax, icms, total

def fetch_usd_ptax():
    try:
        response = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL")
        data = response.json()
        rate = float(data["USDBRL"]["bid"])
        # Trunca para 4 dígitos decimais sem arredondar
        rate = truncate(rate, 4)
        return rate
    except Exception:
        st.error(current_texts["error_cotacao"])
        return None

# ===========================================
# Gerenciamento do Idioma usando st.session_state
# ===========================================
if "lang" not in st.session_state:
    st.session_state.lang = "Português"

def toggle_language():
    languages = ["Português", "English", "中文"]
    current = st.session_state.lang
    idx = languages.index(current)
    st.session_state.lang = languages[(idx + 1) % len(languages)]

# Botão de troca de idioma no canto superior direito
st.markdown(
    """
    <div class="fixed-lang-button">
    """,
    unsafe_allow_html=True
)
if st.button("Trocar Idioma", key="toggle_lang", help="Clique para alternar entre Português, English e 中文"):
    toggle_language()
st.markdown(
    """
    </div>
    """,
    unsafe_allow_html=True
)

lang = st.session_state.lang
current_texts = translations[lang]

# ===========================================
# Interface Principal
# ===========================================
st.title(current_texts["title"])
st.write(current_texts["description"])

# ====== Cotação do USD ======
st.subheader(current_texts["dolar_label"])
auto_cotacao = st.checkbox(current_texts["auto_cotacao"], value=True)
if auto_cotacao:
    cotacao = fetch_usd_ptax()
    if cotacao:
        st.success(f"{format_rate(cotacao, lang)} BRL")
    else:
        cotacao = st.number_input(current_texts["dolar_label"], value=5.0, step=0.0001)
else:
    cotacao = st.number_input(current_texts["dolar_label"], value=5.0, step=0.0001)

# ====== Dados da Remessa ======
st.subheader(current_texts["remessa"])
col1, col2 = st.columns(2)
with col1:
    product_value = st.number_input(current_texts["product"], min_value=0.0, step=0.01, format="%.2f")
    freight_value = st.number_input(current_texts["freight"], min_value=0.0, step=0.01, format="%.2f")
    insurance_value = st.number_input(current_texts["insurance"], min_value=0.0, step=0.01, format="%.2f")
with col2:
    last_mile = st.number_input(current_texts["last_mile"], min_value=0.0, step=0.01, format="%.2f")
    other_expenses = st.number_input(current_texts["other_expenses"], min_value=0.0, step=0.01, format="%.2f")
    volume_anual = st.number_input(current_texts["volume"], min_value=1, step=1, value=1)

base = product_value + freight_value + insurance_value + last_mile + other_expenses
st.markdown(f"**Base Aduaneira (USD):** {format_number(base, lang)}")

# ====== Seleção do Regime ======
st.subheader(current_texts["regime"])
regime = st.radio("", options=[current_texts["prc"], current_texts["rts"]], index=0)

# ====== Cálculos ======
if regime == current_texts["prc"]:
    import_tax, icms, total = calc_prc(base)
    imp_np, icms_np, total_np = calc_no_prc(base)
else:
    import_tax, icms, total = calc_no_prc(base)
    imp_np, icms_np, total_np = calc_prc(base)

import_tax_brl = import_tax * cotacao
icms_brl = icms * cotacao
total_brl = total * cotacao

# ====== Resultados por Remessa ======
st.subheader(current_texts["resultado"])
colA, colB, colC = st.columns(3)
with colA:
    st.metric(f"{current_texts['imp']} (USD)", format_currency(import_tax, "USD", lang))
    st.metric(f"{current_texts['imp']} (BRL)", format_currency(import_tax_brl, "R$", lang))
with colB:
    st.metric(f"{current_texts['icms']} (USD)", format_currency(icms, "USD", lang))
    st.metric(f"{current_texts['icms']} (BRL)", format_currency(icms_brl, "R$", lang))
with colC:
    st.metric(f"{current_texts['total']} (USD)", format_currency(total, "USD", lang))
    st.metric(f"{current_texts['total']} (BRL)", format_currency(total_brl, "R$", lang))

# ====== Projeção Anual ======
st.subheader(current_texts["anual"])
total_anual_usd = total * volume_anual
total_anual_brl = total_brl * volume_anual
st.markdown(f"**{current_texts['custo_anual']} (USD):** {format_currency(total_anual_usd, 'USD', lang)}")
st.markdown(f"**{current_texts['custo_anual']} (BRL):** {format_currency(total_anual_brl, 'R$', lang)}")

# ====== Comparação entre Regimes (Ênfase na Economia com PRC) ======
st.subheader(current_texts["comparacao"])
comparar = st.checkbox("Mostrar comparação")
if comparar:
    import_tax_np_brl = imp_np * cotacao
    icms_np_brl = icms_np * cotacao
    total_np_brl = total_np * cotacao

    st.markdown(f"**Regime comparado: {current_texts['rts'] if regime==current_texts['prc'] else current_texts['prc']}**")
    colX, colY, colZ = st.columns(3)
    with colX:
        st.metric(f"{current_texts['imp']} (USD)", format_currency(imp_np, "USD", lang))
        st.metric(f"{current_texts['imp']} (BRL)", format_currency(import_tax_np_brl, "R$", lang))
    with colY:
        st.metric(f"{current_texts['icms']} (USD)", format_currency(icms_np, "USD", lang))
        st.metric(f"{current_texts['icms']} (BRL)", format_currency(icms_np_brl, "R$", lang))
    with colZ:
        st.metric(f"{current_texts['total']} (USD)", format_currency(total_np, "USD", lang))
        st.metric(f"{current_texts['total']} (BRL)", format_currency(total_np_brl, "R$", lang))
    
    saving_per_shipment = total_np - total  # RTS - PRC para destacar economia com PRC
    saving_annual_usd = saving_per_shipment * volume_anual
    saving_annual_brl = saving_annual_usd * cotacao
    
    if regime == current_texts["prc"]:
        st.info(current_texts["economia"].format(
            usd=format_number(saving_annual_usd, lang),
            brl=format_number(saving_annual_brl, lang)
        ))
    else:
        st.info(current_texts["troca"].format(
            usd=format_number(saving_annual_usd, lang),
            brl=format_number(saving_annual_brl, lang)
        ))

# ====== Exportação dos Resultados ======
st.subheader(current_texts["export"])
df_export = pd.DataFrame({
    "Regime": [regime],
    "Base (USD)": [base],
    "Imp. (USD)": [import_tax],
    "ICMS (USD)": [icms],
    "Total (USD)": [total],
    "Imp. (BRL)": [import_tax_brl],
    "ICMS (BRL)": [icms_brl],
    "Total (BRL)": [total_brl],
    "Volume Anual": [volume_anual],
    "Custo Anual (USD)": [total_anual_usd],
    "Custo Anual (BRL)": [total_anual_brl]
})
csv = df_export.to_csv(index=False).encode("utf-8")
st.download_button(
    label=current_texts["baixar_csv"],
    data=csv,
    file_name="simulacao_prc_rts_comparacao.csv",
    mime="text/csv"
)

st.write("Pronto! Se precisar de mais ajustes, é só avisar.")
