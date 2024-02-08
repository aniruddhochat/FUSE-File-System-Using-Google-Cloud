#Create Virtual Private Cloud (VPC) network
gcloud compute networks create computenetworksani --subnet-mode=auto

#Set Firewall Rules
gcloud compute firewall-rules create default-allow-icmp --network computenetworksani --allow tcp,udp,icmp --source-ranges 0.0.0.0/0
gcloud compute firewall-rules create default-allow-ssh --network computenetworksani --allow tcp:22 --source-ranges 0.0.0.0/0
gcloud compute firewall-rules create default-allow-internal --network computenetworksani --allow tcp:22,tcp:3389,3200,icmp
gcloud compute firewall-rules create default-allow-external --network computenetworksani --allow tcp:23,tcp:3388,icmp


#Create Fuse VM
gcloud compute instances create fuse-fs --project=aniruddho-chatterjee-fall2023 --zone=us-east4-c --machine-type=e2-medium --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=computenetworksani --maintenance-policy=MIGRATE --provisioning-model=STANDARD --service-account=479686037232-compute@developer.gserviceaccount.com --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append --tags=http-server,https-server,lb-health-check --create-disk=auto-delete=yes,boot=yes,device-name=kvs-server,image=projects/debian-cloud/global/images/debian-11-bullseye-v20230912,mode=rw,size=10,type=projects/aniruddho-chatterjee-fall2023/zones/us-central1-a/diskTypes/pd-balanced --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --labels=goog-ec-src=vm_add-gcloud --reservation-affinity=any


sudo ./installRequirements.sh
echo "Installation completed successfully."