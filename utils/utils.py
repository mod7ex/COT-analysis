import plotly.express as px
from pandas import DataFrame

def plot_df_line_chart(
        df = DataFrame(),
        chart_title: str = "Chart Title",
        draw = True,
        save_to_html = False,
        save_file_name = "plot",
        use_markers= True
):
    fig = px.line(df, markers=True)

    fig.update_layout(
        title=chart_title,
        template="plotly_dark",
        paper_bgcolor="black",
        plot_bgcolor="black",
        # width=1500,
        height=800,

        # hovermode="x unified",  # one vertical hover line
        dragmode="zoom",

        font=dict(color="white", size=12),

        legend=dict(
            itemclick="toggle",        # click = hide/show
            itemdoubleclick="toggleothers",
            bgcolor="rgba(0,0,0,0)"
        ),

        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            rangeslider=dict(visible=True),  # 🔥 range slider
        ),

        yaxis=dict(
            title='Contracts',
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            fixedrange=False
        )
    )

    fig.update_traces(
        mode=f"lines{'+markers' if use_markers else ''}",
        line=dict(width=1),
        hovertemplate="<b>%{fullData.name}</b><br>%{y:.2f}<extra></extra>"
    )

    if save_to_html: fig.write_html(f"plots/{save_file_name}.html")

    if draw: return fig.show()
    else: return fig