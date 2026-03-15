import streamlit as st

st.set_page_config(page_title="Nando CSV Validator", layout="wide")

st.title("🔍 Validador de Estrutura CSV")
st.markdown("Verificação de integridade para arquivos de grande volume.")

uploaded_file = st.file_uploader("Suba seu arquivo CSV", type="csv")

if uploaded_file:
    # 1. Configuração Inicial (Header e Separador)
    # Lemos a primeira linha para definir o padrão
    primeira_linha = uploaded_file.readline().decode("utf-8").strip()
    
    # Detecta o separador com base na frequência
    sep = ";" if primeira_linha.count(";") > primeira_linha.count(",") else ","
    
    colunas_header = primeira_linha.split(sep)
    qtd_esperada = len(colunas_header)
    
    st.info(f"**Configuração Detectada:** Separador [ `{sep}` ] | Colunas no Header: **{qtd_esperada}**")
    
    # Voltamos o ponteiro para o início para validar tudo, incluindo o header
    uploaded_file.seek(0)

    if st.button("Iniciar Processamento"):
        erros = []
        total_linhas = 0
        
        progress_bar = st.progress(0)
        status_msg = st.empty()

        # 2. Loop de Processamento (Eficiente em RAM)
        for idx, linha_binaria in enumerate(uploaded_file):
            total_linhas += 1
            linha_texto = linha_binaria.decode("utf-8").strip()
            
            if not linha_texto:
                continue
                
            # Validação da estrutura
            colunas_da_linha = linha_texto.split(sep)
            if len(colunas_da_linha) != qtd_esperada:
                erros.append({
                    "linha": idx + 1,
                    "esperado": qtd_esperada,
                    "encontrado": len(colunas_da_linha),
                    "conteudo": linha_texto[:60] # Mostra apenas o início para não poluir
                })
            
            # Atualiza interface a cada 50k linhas
            if total_linhas % 50000 == 0:
                status_msg.text(f"Processadas: {total_linhas:,} linhas...")

        progress_bar.progress(100)
        status_msg.text("Processamento concluído!")

        # 3. Painel de Resultados
        st.divider()
        col1, col2 = st.columns(2)
        col1.metric("Total de Linhas Processadas", f"{total_linhas:,}")
        col2.metric("Linhas com Erro", f"{len(erros):,}", delta=len(erros), delta_color="inverse")

        if not erros:
            st.success(f"✅ Excelente! Todas as {total_linhas:,} linhas estão estruturalmente corretas.")
        else:
            st.error(f"⚠️ Atenção: Foram detectadas {len(erros)} inconsistências.")
            
            # Preparar relatório para download
            relatorio_texto = f"RELATÓRIO DE ERROS - NANDO CSV TOOL\n"
            relatorio_texto += f"Total de linhas analisadas: {total_linhas}\n"
            relatorio_texto += f"Total de erros encontrados: {len(erros)}\n"
            relatorio_texto += "="*50 + "\n\n"
            
            for e in erros:
                relatorio_texto += f"Linha {e['linha']}: Esperava {e['esperado']} colunas, encontrou {e['encontrado']} colunas. Conteúdo: {e['conteudo']}\n"
            
            st.download_button(
                label="📥 Baixar Lista Completa de Erros (.txt)",
                data=relatorio_texto,
                file_name="erros_validacao_csv.txt",
                mime="text/plain"
            )

            with st.expander("Ver as primeiras linhas com erro"):
                for e in erros[:100]:
                    st.write(f"**Linha {e['linha']}**: {e['conteudo']}")