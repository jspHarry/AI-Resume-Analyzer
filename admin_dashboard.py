from data_insertion import fetch_all_users  # Import function

data = fetch_all_users()  # Fetch data from MongoDB
df = pd.DataFrame(data)  # Convert to DataFrame for displaying
st.dataframe(df)  # Display
