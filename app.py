
import os
import json
from io import BytesIO

import boto3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from botocore.exceptions import ClientError

st.set_page_config(page_title="ECG Analysis Dashboard", page_icon="❤️", layout="wide")

st.title("❤️ ECG Analysis in the Cloud")
st.write("ECG data and analysis results retrieved from Amazon S3.")

BUCKET_NAME = "ecg-analysis-batch8-2026"
AWS_REGION = "eu-north-1"

@st.cache_resource
def get_s3_client():
    access_key = st.secrets.get(
        "AWS_ACCESS_KEY_ID", os.environ.get("AWS_ACCESS_KEY_ID")
    )
    secret_key = st.secrets.get(
        "AWS_SECRET_ACCESS_KEY", os.environ.get("AWS_SECRET_ACCESS_KEY")
    )

    if not access_key or not secret_key:
        raise RuntimeError("AWS credentials are not configured.")

    return boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

try:
    s3 = get_s3_client()

    response = s3.get_object(Bucket=BUCKET_NAME, Key="sample_ecg.csv")
    df = pd.read_csv(BytesIO(response["Body"].read()))

    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key="results/ecg_analysis_results.json",
    )
    results = json.loads(response["Body"].read().decode("utf-8"))

    st.success("Successfully connected to Amazon S3.")

    col1, col2, col3 = st.columns(3)
    col1.metric("ECG Samples", results["total_samples"])
    col2.metric("Detected Peaks", results["detected_peaks"])
    col3.metric("Estimated Heart Rate", f'{results["estimated_heart_rate_bpm"]} BPM')

    st.subheader("ECG Waveform")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df["time_seconds"], df["ecg_amplitude"])
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Amplitude")
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Analysis Details")
    st.json(results)
    st.caption("Educational demonstration using simulated ECG data; not intended for medical diagnosis.")

except ClientError as e:
    st.error(f"AWS error: {e.response['Error']['Code']}. Check bucket, object keys, and IAM permissions.")
except Exception as e:
    st.error(f"Unable to load dashboard data: {e}")
