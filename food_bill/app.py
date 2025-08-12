import streamlit as st
from io import BytesIO
import tempfile
import os

# Function to handle file upload
def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        # Create a temporary file to save the uploaded content
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        st.session_state.uploaded_file_path = tmp_file_path
        st.success("File uploaded successfully!")
        st.write(f"File saved at: {tmp_file_path}")
    else:
        st.error("No file uploaded.")

# Function to process the reimbursement
def process_reimbursement(employee_id, employee_name, claimed_amount, receipt_path):
    # Implement your backend processing logic here
    # For demonstration, we'll just return a mock result
    return {
        "status": "approved",
        "message": f"Reimbursement for {employee_name} ({employee_id}) approved for ₹{claimed_amount}.",
        "receipt_path": receipt_path
    }

# Function to display the form and process inputs
def display_form():
    with st.form(key='reimbursement_form'):
        st.subheader("Employee Information")
        employee_id = st.text_input("Employee ID")
        employee_name = st.text_input("Employee Name")
        claimed_amount = st.number_input("Claimed Amount", min_value=0.0, format="%.2f")
        receipt_file = st.file_uploader("Upload Receipt", type=["jpg", "jpeg", "png", "pdf"])

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if receipt_file:
                handle_file_upload(receipt_file)
            else:
                st.error("Please upload a receipt file.")

            if employee_id and employee_name and claimed_amount and 'uploaded_file_path' in st.session_state:
                # Call the backend processing function
                st.write("Processing reimbursement...")
                result = process_reimbursement(employee_id, employee_name, claimed_amount, st.session_state.uploaded_file_path)
                st.write(result["message"])
                st.image(result["receipt_path"])
            else:
                st.error("Please fill in all fields and upload a receipt.")

# Main app flow
def main():
    st.title("Food Bill Reimbursement Portal")
    display_form()

if __name__ == "__main__":
    main()
