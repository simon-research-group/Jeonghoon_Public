#command for deployment into Google Cloud 

gcloud builds submit --tag gcr.io/turb-si-interactive-zcrit/turb-si-interactive-zcrit-plot  --project=turb-si-interactive-zcrit

gcloud run deploy --image gcr.io/turb-si-interactive-zcrit/turb-si-interactive-zcrit-plot --platform managed  --project=turb-si-interactive-zcrit --allow-unauthenticated
