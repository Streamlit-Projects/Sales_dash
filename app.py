import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl

st.set_page_config( page_title='Sales Dashboard'
                  , page_icon=':bar_chart:'
                  , layout='wide'
                  )


@st.cache
def get_data_from_excel():
    df = pd.read_excel( io='supermarket_sales.xlsx'
                      , engine='openpyxl'
                      , sheet_name='Sales'
                      , skiprows=3
                      , usecols='B:R'
                      , nrows=1000
                      )
    df['hour']=pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour
    return df

df=get_data_from_excel()


st.sidebar.header('Please filter here:')
city=st.sidebar.multiselect('Select the city:'
                           , options=df['City'].unique()
                           , default=df['City'].unique()
                           )

customer_type=st.sidebar.multiselect('Select the customer type'
                                    , options=df['Customer_type'].unique()
                                    , default=df['Customer_type'].unique()
                                    )

gender=st.sidebar.multiselect('Select the gender:'
                             , options=df['Gender'].unique()
                             , default=df['Gender'].unique()
                             )

df_selection = df.query("City==@city & Customer_type==@customer_type & Gender==@gender")

# Page title:
st.title(':bar_chart: Sales Dashboard')
st.markdown('##')

# Define KPI(s):
total_sales=int(df_selection['Total'].sum())
average_rating=round(df_selection['Rating'].mean(),1)
star_rating=':star:' * int(round(average_rating,0))
avg_sale_transactional=round(df_selection['Total'].mean(),2)

# Display KPI(s):
left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.markdown('#### Total Sales:')
    st.markdown(f'US ${total_sales:,}')
with middle_column:
    st.markdown('#### Average Rating:')
    st.markdown(f'{average_rating} {star_rating}')
with right_column:
    st.markdown('#### Avg. Sales by Transaction:')
    st.markdown(f'US ${avg_sale_transactional}')

st.markdown("""___""")

# Sales by product (bar chart):
sales_by_product_line=(df_selection.groupby(by=['Product line']).sum()[['Total']].sort_values(by='Total'))

fig_product_sales=px.bar(sales_by_product_line
                        , x='Total'
                        , y=sales_by_product_line.index
                        , orientation='h'
                        , title="<b>Sales by Product Line</b>"
                        , color_discrete_sequence=['#0083B8'] * len(sales_by_product_line)
                        , template='plotly_white'
                        )
fig_product_sales.update_layout( plot_bgcolor='rgba(0,0,0,0)'
                               , xaxis=(dict(showgrid=False))
                               , yaxis=(dict(ticksuffix = "   "))
                               )

# Sales by hour (bar chart):
sales_by_hour = df_selection.groupby(by=['hour']).sum()[['Total']]

fig_hourly_sales=px.bar(sales_by_hour
                       , x=sales_by_hour.index
                       , y='Total'
                       , title='<b>Sales by hour</b>'
                       , color_discrete_sequence=['#0083B8'] * len(sales_by_hour)
                       , template='plotly_white'
                       )
fig_hourly_sales.update_layout( plot_bgcolor='rgba(0,0,0,0)'
                              , xaxis=dict(tickmode='linear')
                              , yaxis=dict(showgrid=False, ticksuffix = "   "))


# Plug graphs into columns:
left_column, right_column=st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)

# Hide streamlit style:
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
