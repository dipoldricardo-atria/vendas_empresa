import io # Para processar o arquivo na memória

# --- DENTRO DO BLOCO 'IF MENU == "Dashboard":' ---
st.markdown("---")
st.subheader("🏁 Fechamento de Mês para o Financeiro")

# Seleção de Mês e Ano para o Relatório
col_mes, col_ano, col_btn = st.columns([2, 2, 3])
mes_sel = col_mes.selectbox("Mês", list(range(1, 13)), index=datetime.now().month - 1)
ano_sel = col_ano.selectbox("Ano", [2024, 2025, 2026], index=2) # Index 2 = 2026

if col_btn.button("Gerar Relatório de Comissões"):
    # Filtrar parcelas PAGAS no mês/ano selecionado
    # (Considerando que a data da parcela é quando o dinheiro caiu)
    query = f"SELECT vendedor, cliente, tipo, valor, comissao, data FROM parcelas WHERE status='Pago'"
    df_relatorio = pd.read_sql(query, conn)
    
    # Converter data para filtrar por mês/ano
    df_relatorio['data'] = pd.to_datetime(df_relatorio['data'])
    df_final = df_relatorio[(df_relatorio['data'].dt.month == mes_sel) & 
                            (df_relatorio['data'].dt.year == ano_sel)]

    if not df_final.empty:
        # Criar arquivo Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Comissoes')
            
            # Formatação visual básica no Excel
            workbook  = writer.book
            worksheet = writer.sheets['Comissoes']
            format_moeda = workbook.add_format({'num_format': 'R$ #,##0.00'})
            worksheet.set_column('D:E', 15, format_moeda) # Colunas Valor e Comissão
            worksheet.set_column('A:C', 20)
            
        st.success(f"Relatório de {mes_sel}/{ano_sel} gerado com sucesso!")
        st.download_button(
            label="📥 Baixar Excel para o Financeiro",
            data=output.getvalue(),
            file_name=f"Fechamento_Comissoes_{mes_sel}_{ano_sel}.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.warning("Não há comissões pagas neste período para exportar.")