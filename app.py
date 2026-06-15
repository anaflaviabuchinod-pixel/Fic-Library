import os
import uuid

import pandas as pd
import streamlit as st


ARQUIVO = "leituras.csv"

COLUNAS = [
    "id",
    "leitura",
    "site",
    "tags",
    "nota",
    "observacoes",
]


def criar_base_vazia():
    return pd.DataFrame(columns=COLUNAS)


def carregar_dados():
    if not os.path.exists(ARQUIVO):
        df = criar_base_vazia()
        df.to_csv(ARQUIVO, index=False)
        return df

    try:
        df = pd.read_csv(ARQUIVO)
    except pd.errors.EmptyDataError:
        return criar_base_vazia()

    for coluna in COLUNAS:
        if coluna not in df.columns:
            df[coluna] = 0 if coluna == "nota" else ""

    df = df[COLUNAS].copy()

    df["id"] = df["id"].fillna("").astype(str)
    df["leitura"] = df["leitura"].fillna("").astype(str)
    df["site"] = df["site"].fillna("").astype(str)
    df["tags"] = df["tags"].fillna("").astype(str)
    df["observacoes"] = df["observacoes"].fillna("").astype(str)

    df["nota"] = pd.to_numeric(df["nota"], errors="coerce").fillna(0).astype(int)
    df["nota"] = df["nota"].clip(0, 5)

    for i in df.index:
        if df.at[i, "id"].strip() == "":
            df.at[i, "id"] = str(uuid.uuid4())

    return df.reset_index(drop=True)


def limpar_dados(df):
    df = df.copy()

    if "estrelas" in df.columns:
        df = df.drop(columns=["estrelas"])

    for coluna in COLUNAS:
        if coluna not in df.columns:
            df[coluna] = 0 if coluna == "nota" else ""

    df = df[COLUNAS].copy()

    df["id"] = df["id"].fillna("").astype(str)
    df["leitura"] = df["leitura"].fillna("").astype(str)
    df["site"] = df["site"].fillna("").astype(str)
    df["tags"] = df["tags"].fillna("").astype(str)
    df["observacoes"] = df["observacoes"].fillna("").astype(str)

    df["nota"] = pd.to_numeric(df["nota"], errors="coerce").fillna(0).astype(int)
    df["nota"] = df["nota"].clip(0, 5)

    df = df[
        df["leitura"].str.strip().ne("")
        | df["site"].str.strip().ne("")
        | df["tags"].str.strip().ne("")
        | df["observacoes"].str.strip().ne("")
    ].copy()

    for i in df.index:
        if df.at[i, "id"].strip() == "":
            df.at[i, "id"] = str(uuid.uuid4())

    return df.reset_index(drop=True)


def salvar_dados(df):
    df = limpar_dados(df)
    df.to_csv(ARQUIVO, index=False)


def separar_tags(texto):
    if pd.isna(texto) or str(texto).strip() == "":
        return []

    return [
        tag.strip().lower()
        for tag in str(texto).split(",")
        if tag.strip()
    ]


def listar_tags(df):
    tags = []

    if df.empty:
        return []

    for item in df["tags"].fillna(""):
        tags.extend(separar_tags(item))

    return sorted(set(tags))


def estrelas(nota):
    nota = int(nota)
    return "★" * nota + "☆" * (5 - nota)


st.set_page_config(
    page_title="Alexandria Fic Library",
    page_icon="💜",
    layout="wide",
)


st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #F5EDFF 0%, #FBF8FF 45%, #E9D5FF 100%);
    }

    .hero {
        background: rgba(255,255,255,0.86);
        border: 1px solid rgba(126, 34, 206, 0.18);
        border-radius: 28px;
        padding: 32px 36px;
        box-shadow: 0 14px 36px rgba(88, 28, 135, 0.12);
        margin-bottom: 28px;
    }

    .hero-title {
        font-size: 44px;
        font-weight: 900;
        color: #4C1D95;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        color: #6D28D9;
        font-size: 17px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 850;
        color: #4C1D95;
        margin-top: 24px;
        margin-bottom: 12px;
    }

    .tag-chip {
        display: inline-block;
        background-color: #E9D5FF;
        color: #581C87;
        border: 1px solid #C084FC;
        padding: 7px 13px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 700;
        margin: 4px;
    }

    div[data-testid="stMetric"] {
        background-color: rgba(255,255,255,0.88);
        border: 1px solid rgba(126, 34, 206, 0.16);
        border-radius: 20px;
        padding: 16px;
        box-shadow: 0 8px 22px rgba(88, 28, 135, 0.08);
    }

    section[data-testid="stSidebar"] {
        background-color: #EDE4FF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="hero">
        <div class="hero-title">💜📚 Alexandria Fic Library 🔮✨</div>
        <div class="hero-subtitle">
            Organize suas fics, links, tags, notas e observações em uma biblioteca lilás.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


df = carregar_dados()

todas_tags = listar_tags(df)

col1, col2, col3, col4 = st.columns(4)

col1.metric("📚 Total de leituras", len(df))
col2.metric("🏷️ Tags cadastradas", len(todas_tags))
col3.metric("🔗 Com link", df["site"].str.strip().ne("").sum())

nota_media = df["nota"].mean() if len(df) > 0 else 0
col4.metric("💜 Nota média", f"{nota_media:.1f}/5")


st.markdown('<div class="section-title">🏷️🔮 Filtro por tags</div>', unsafe_allow_html=True)

tags_escolhidas = st.multiselect(
    "Selecione uma ou mais tags",
    options=todas_tags,
)

if todas_tags:
    tags_html = ""
    for tag in todas_tags:
        tags_html += f'<span class="tag-chip">💜 {tag}</span>'

    st.markdown(tags_html, unsafe_allow_html=True)


df_filtrado = df.copy()

if tags_escolhidas:
    df_filtrado = df_filtrado[
        df_filtrado["tags"].apply(
            lambda texto: any(tag in separar_tags(texto) for tag in tags_escolhidas)
        )
    ]


st.markdown('<div class="section-title">📚💜 Leituras</div>', unsafe_allow_html=True)

st.info(
    "Edite direto na tabela. Para adicionar uma nova leitura, preencha a linha vazia no final. "
    "Depois clique em 💾 Salvar alterações."
)

df_tabela = df_filtrado.copy()
df_tabela["estrelas"] = df_tabela["nota"].apply(estrelas)

df_editado = st.data_editor(
    df_tabela,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    column_order=[
        "leitura",
        "site",
        "tags",
        "nota",
        "estrelas",
        "observacoes",
    ],
    column_config={
        "leitura": st.column_config.TextColumn("📖 Leitura / fic"),
        "site": st.column_config.LinkColumn("🔗 Site"),
        "tags": st.column_config.TextColumn(
            "🏷️ Tags",
            help="Separe as tags por vírgula. Ex: tbr, fav, wip",
        ),
        "nota": st.column_config.NumberColumn(
            "💜 Nota",
            min_value=0,
            max_value=5,
            step=1,
        ),
        "estrelas": st.column_config.TextColumn("✨ Estrelas", disabled=True),
        "observacoes": st.column_config.TextColumn("📝 Observações"),
    },
)


col_salvar, col_apagar = st.columns([1, 5])

with col_salvar:
    salvar = st.button("💾 Salvar alterações")

with col_apagar:
    apagar = st.button("🗑️ Apagar tudo")


if salvar:
    df_editado_limpo = limpar_dados(df_editado)

    if tags_escolhidas:
        ids_filtrados = df_filtrado["id"].tolist()
        df_restante = df[~df["id"].isin(ids_filtrados)]
        df_final = pd.concat([df_restante, df_editado_limpo], ignore_index=True)
    else:
        df_final = df_editado_limpo.copy()

    salvar_dados(df_final)

    st.success("Alterações salvas! 💜✨")
    st.rerun()


if apagar:
    salvar_dados(criar_base_vazia())
    st.warning("Tudo foi apagado.")
    st.rerun()


st.markdown('<div class="section-title">💜 Avaliação por estrelas</div>', unsafe_allow_html=True)

df_atual = carregar_dados()

if df_atual.empty:
    st.info("Nenhuma leitura cadastrada ainda.")
else:
    df_estrelas = df_atual[["leitura", "nota"]].copy()
    df_estrelas["estrelas"] = df_estrelas["nota"].apply(estrelas)
    st.dataframe(df_estrelas, use_container_width=True, hide_index=True)


st.caption("💜 Feito com Python + Streamlit.")