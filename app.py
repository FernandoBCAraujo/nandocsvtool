import streamlit as st

# Configurações iniciais
st.set_page_config(page_title="Nando CSV Tool", layout="wide", page_icon="🔍")

# --- FUNÇÕES DE SUPORTE ---
def corrigir_estrutura_csv(file_buffer, separador, total_colunas_esperado):
    output = []
    file_buffer.seek(0)
    for linha_binaria in file_buffer:
        linha_texto = linha_binaria.decode("utf-8").strip()
        if not linha_texto:
            continue
        contagem_atual = linha_texto.count(separador)
        objetivo = total_colunas_esperado - 1
        if contagem_atual < objetivo:
            linha_texto += (separador * (objetivo - contagem_atual))
        output.append(linha_texto)
    return "\n".join(output)

# --- INTERFACE ---
st.title("🛠️ Nando CSV Tool")

# Criando abas para organizar o serviço
tab_validador, tab_corretor = st.tabs(["🧐 Validador de Estrutura", "🔧 Corretor de Colunas"])

with tab_validador:
    uploaded_file = st.file_uploader("Suba seu arquivo CSV para análise", type="csv", key="validador")

    if uploaded_file:
        # Identificação de padrão
        primeira_linha = uploaded_file.readline().decode("utf-8").strip()
        sep = ";" if primeira_linha.count(";") > primeira_linha.count(",") else ","
        qtd_esperada = len(primeira_linha.split(sep))
        uploaded_file.seek(0)

        st.info(f"Separador: `{sep}` | Colunas esperadas: **{qtd_esperada}**")

        if st.button("Iniciar Validação"):
            erros = []
            total = 0
            for idx, linha in enumerate(uploaded_file):
                total += 1
                txt = linha.decode("utf-8").strip()
                if not txt: continue
                if len(txt.split(sep)) != qtd_esperada:
                    erros.append(f"Linha {idx+1}: {txt[:50]}...")
            
            # Guardando no session_state para não perder ao clicar em botões
            st.session_state['erros'] = erros
            st.session_state['total'] = total
            st.session_state['sep'] = sep
            st.session_state['qtd'] = qtd_esperada

        # Exibição de Resultados (se existirem no estado)
        if 'erros' in st.session_state:
            st.divider()
            c1, c2 = st.columns(2)
            c1.metric("Linhas Processadas", st.session_state['total'])
            c2.metric("Inconsistências", len(st.session_state['erros']), delta=len(st.session_state['erros']), delta_color="inverse")

            if st.session_state['erros']:
                st.error("Clique na aba **Corretor de Colunas** para baixar uma versão corrigida.")
                with st.expander("Ver logs de erro"):
                    st.write(st.session_state['erros'][:100])

with tab_corretor:
    st.subheader("Ajuste automático de linhas")
    if 'erros' in st.session_state and len(st.session_state['erros']) > 0:
        st.write(f"Detectamos {len(st.session_state['erros'])} linhas curtas. Deseja completar com `{st.session_state['sep']}`?")
        
        if st.button("Gerar Arquivo Corrigido"):
            with st.spinner("Reestruturando linhas..."):
                # Usamos o arquivo que ainda está no buffer do uploader
                csv_fix = corrigir_estrutura_csv(uploaded_file, st.session_state['sep'], st.session_state['qtd'])
                st.success("Arquivo pronto!")
                st.download_button(
                    label="⬇️ Baixar CSV Corrigido",
                    data=csv_fix,
                    file_name="corrigido_nandotools.csv",
                    mime="text/csv"
                )
    else:
        st.info("Nenhum erro de coluna curta detectado ou arquivo ainda não validado.")