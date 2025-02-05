import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Load the dataset
all_df = pd.read_csv("dashboard/main_data.csv")

# Check for required columns
required_columns = ["order_purchase_timestamp", "order_id", "total_order_price", 
                    "customer_city", "customer_state", "review_comment_value", 
                    "approval_time_diff", "delivery_time_diff", "on_time_delivery", 
                    "review_score", "review_category", "product_category_name_english", 
                    "customer_id"]
missing_columns = [col for col in required_columns if col not in all_df.columns]
if missing_columns:
    st.error(f"Missing columns in dataset: {', '.join(missing_columns)}")
    st.stop()

# Ensure date columns are in datetime format
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])

# Sidebar configuration
with st.sidebar:
    st.image("https://superawesomevectors.com/wp-content/uploads/2016/05/calendar-flat-vector-icon-800x566.jpg")
    min_date = all_df["order_purchase_timestamp"].min()
    max_date = all_df["order_purchase_timestamp"].max()
    try:
        start_date, end_date = st.date_input(
            label='Rentang Waktu', 
            min_value=min_date, 
            max_value=max_date, 
            value=[min_date, max_date]
        )
    except Exception as e:
        st.warning("Terjadi kesalahan dalam memilih rentang tanggal. Menggunakan nilai default.")
        start_date, end_date = min_date, max_date

main_df = all_df[
    (all_df["order_purchase_timestamp"] >= pd.Timestamp(start_date)) & 
    (all_df["order_purchase_timestamp"] <= pd.Timestamp(end_date))
]

st.header("E-Commerce Revenue Dashboard 💵")

# Monthly Orders and Revenue
st.subheader("Monthly Orders and Revenue")
monthly_orders_df = main_df.resample(rule='M', on='order_purchase_timestamp').agg({
    "order_id": "nunique",
    "total_order_price": "sum"
}).reset_index()

monthly_orders_df["order_purchase_timestamp"] = monthly_orders_df["order_purchase_timestamp"].dt.strftime('%Y-%B')
monthly_orders_df.rename(columns={
    "order_purchase_timestamp": "order_date",
    "order_id": "order_count",
    "total_order_price": "revenue"
}, inplace=True)

col1, col2 = st.columns(2)
 
with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "BRL", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)

plt.style.use("dark_background")  # atau 'seaborn-dark'

# Jika ingin memastikan background tetap transparan
fig, ax = plt.subplots()
ax.set_facecolor("none")  # Menghapus background pada area plot
fig.patch.set_alpha(0)  # Menghapus background figure
plt.figure(figsize=(10, 5))
plt.plot(
    monthly_orders_df["order_date"],
    monthly_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#72BCD4"
)
plt.title("Number of Orders per Month", loc="center", fontsize=16)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Number of Orders", fontsize=12)
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)
plt.grid(visible=True, linestyle="--", alpha=0.6)
st.pyplot(plt)

plt.figure(figsize=(10, 5))
plt.plot(
    monthly_orders_df["order_date"],
    monthly_orders_df["revenue"],
    marker='o',
    linewidth=2,
    color="#72BCD4"
)
plt.title("Total Revenue per Month", loc="center", fontsize=16)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Total Revenue (Currency)", fontsize=12)
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)
plt.grid(visible=True, linestyle="--", alpha=0.6)
st.pyplot(plt)

# Top 4 Cities by Customer Count
st.subheader("Top 4 Cities by Customer Count")
bycity_df = main_df.groupby(by="customer_city").customer_id.nunique().reset_index()
bycity_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
top_city = bycity_df.sort_values(by="customer_count", ascending=False).iloc[0]

st.metric("Top City", value=top_city["customer_city"])

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="customer_count", x="customer_city", data=bycity_df.sort_values(by="customer_count", ascending=False).head(4), palette="Blues_d", ax=ax)
ax.set_title("Top 4 Cities with Most Customers", fontsize=16)
ax.set_xlabel("City", fontsize=12)
ax.set_ylabel("Customer Count", fontsize=12)
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# Top 4 States by Customer Count
st.subheader("Top 4 States by Customer Count")
bystate_df = main_df.groupby(by="customer_state").customer_id.nunique().reset_index()
bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
top_state = bystate_df.sort_values(by="customer_count", ascending=False).iloc[0]

st.metric("Top State", value=top_state["customer_state"])

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="customer_count", x="customer_state", data=bystate_df.sort_values(by="customer_count", ascending=False).head(4), palette="Blues_d", ax=ax)
ax.set_title("Top 4 States with Most Customers", fontsize=16)
ax.set_xlabel("State", fontsize=12)
ax.set_ylabel("Customer Count", fontsize=12)
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# Review Comment Value Distribution
st.subheader("Review Comment Value Distribution")
review_counts = main_df["review_comment_value"].value_counts()
st.metric("Most Frequent Review Comment Value", value=review_counts.idxmax())

fig, ax = plt.subplots(figsize=(8, 6))
sns.countplot(data=main_df, x="review_comment_value", palette="viridis", ax=ax)
ax.set_title("Distribution of Review Comment Value", fontsize=16)
st.pyplot(fig)

# Approval and Delivery Time Analysis
st.subheader("Approval and Delivery Time Analysis")
col1, col2 = st.columns(2)

with col1:
    avg_approval_time = main_df["approval_time_diff"].mean()
    st.metric("Average Approval Time", value=f"{avg_approval_time:.2f} hours")

with col2:
    avg_delivery_time = main_df["delivery_time_diff"].mean()
    st.metric("Average Delivery Time", value=f"{avg_delivery_time:.2f} days")

# Average Approval and Delivery Time Differences
st.subheader("Approval and Delivery Time Analysis")
main_df['month_year'] = main_df['order_purchase_timestamp'].dt.to_period('M')

approval_time_diff_df = main_df.groupby('month_year')['approval_time_diff'].mean().reset_index()
delivery_time_diff_df = main_df.groupby('month_year')['delivery_time_diff'].mean().reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(
    approval_time_diff_df['month_year'].astype(str), 
    approval_time_diff_df['approval_time_diff'], 
    marker='o', 
    linewidth=2, 
    color="turquoise"
)
ax.set_title("Average Approval Time Difference per Month", fontsize=16)
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Average Approval Time (Hours)", fontsize=12)
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(
    delivery_time_diff_df['month_year'].astype(str), 
    delivery_time_diff_df['delivery_time_diff'], 
    marker='o', 
    linewidth=2, 
    color="red"
)
ax.set_title("Average Delivery Time Difference per Month", fontsize=16)
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Average Delivery Time (Days)", fontsize=12)
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# On-Time Delivery Distribution
st.subheader("On-Time Delivery Analysis")
fig, ax = plt.subplots(figsize=(8, 6))
sns.countplot(data=main_df, x="on_time_delivery", palette="viridis", ax=ax)
ax.set_title("On-Time Delivery Distribution", fontsize=16)
ax.set_xlabel("On-Time Delivery (Yes/No)", fontsize=12)
ax.set_ylabel("Frequency", fontsize=12)
st.pyplot(fig)

st.subheader("Clustering Review Category")

# Pastikan kategori review dibuat dari main_df, bukan all_df
score_bins = [0, 2, 3, 5]  # Batas-batas untuk kategorisasi
score_labels = ["Not Satisfied", "Neutral", "Satisfied"]  # Label kategori
main_df['review_category'] = pd.cut(main_df['review_score'], bins=score_bins, labels=score_labels)

# Tampilkan metrik
satisfied_count = (main_df['review_category'] == "Satisfied").sum()
neutral_count = (main_df['review_category'] == "Neutral").sum()
not_satisfied_count = (main_df['review_category'] == "Not Satisfied").sum()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Satisfied Customers", value=satisfied_count)
with col2:
    st.metric("Neutral Customers", value=neutral_count)
with col3:
    st.metric("Not Satisfied Customers", value=not_satisfied_count)

# Pastikan plot menggunakan main_df
plt.figure(figsize=(10, 6))
sns.countplot(data=main_df, x="review_category", palette="viridis")
plt.title("Distribution of Review Categories", loc="center", fontsize=16)
plt.ylabel("Frequency", fontsize=12)
plt.xlabel("Review Category", fontsize=12)
plt.xticks(rotation=45)
st.pyplot(plt)

# Menambahkan kolom untuk status kepuasan berdasarkan review_score
main_df['customer_satisfaction'] = main_df['review_score'].apply(lambda x: 'Satisfied' if x >= 4 else ('Dissatisfied' if x <= 2 else 'Neutral'))

# Mengelompokkan data berdasarkan product_category_name_english dan customer_satisfaction
category_satisfaction_df = main_df.groupby(['product_category_name_english', 'customer_satisfaction']).size().reset_index(name='count')

# Kategori yang paling membuat pelanggan tidak puas (Skor 1 dan 2)
dissatisfied_category_df = category_satisfaction_df[category_satisfaction_df['customer_satisfaction'] == 'Dissatisfied'].sort_values(by='count', ascending=False).head(10)

# Kategori yang paling membuat pelanggan puas (Skor 4 dan 5)
satisfied_category_df = category_satisfaction_df[category_satisfaction_df['customer_satisfaction'] == 'Satisfied'].sort_values(by='count', ascending=False).head(10)

# Top Satisfied and Dissatisfied Product Categories
st.subheader("Product Satisfaction Analysis")
main_df['customer_satisfaction'] = main_df['review_score'].apply(lambda x: 'Satisfied' if x >= 4 else ('Dissatisfied' if x <= 2 else 'Neutral'))
category_satisfaction_df = main_df.groupby(['product_category_name_english', 'customer_satisfaction']).size().reset_index(name='count')
top_satisfied_product = category_satisfaction_df[category_satisfaction_df['customer_satisfaction'] == 'Satisfied'].nlargest(1, 'count')
top_dissatisfied_product = category_satisfaction_df[category_satisfaction_df['customer_satisfaction'] == 'Dissatisfied'].nlargest(1, 'count')


col1, col2 = st.columns(2)
with col1:
    st.metric("Most Satisfied Product", value=top_satisfied_product.iloc[0]['product_category_name_english'])
    st.metric("Satisfied Cases", value=top_satisfied_product.iloc[0]['count'])

with col2:
    st.metric("Most Dissatisfied Product", value=top_dissatisfied_product.iloc[0]['product_category_name_english'])
    st.metric("Dissatisfied Cases", value=top_dissatisfied_product.iloc[0]['count'])

# Top 10 Product Categories with Most Satisfied Customers
st.subheader("Top 10 Product Categories with Most Satisfied Customers")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=satisfied_category_df, x='count', y='product_category_name_english', palette='Blues_d', ax=ax)
ax.set_title("Top 10 Product Categories with Most Satisfied Customers", fontsize=16)
ax.set_xlabel("Number of Satisfied Reviews", fontsize=12)
ax.set_ylabel("Product Category", fontsize=12)
st.pyplot(fig)

# Top 10 Product Categories with Most Dissatisfied Customers
st.subheader("Top 10 Product Categories with Most Dissatisfied Customers")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=dissatisfied_category_df, x='count', y='product_category_name_english', palette='Reds_d', ax=ax)
ax.set_title("Top 10 Product Categories with Most Dissatisfied Customers", fontsize=16)
ax.set_xlabel("Number of Dissatisfied Reviews", fontsize=12)
ax.set_ylabel("Product Category", fontsize=12)
st.pyplot(fig)

st.caption('Copyright (c) Harya.Inc 2025')