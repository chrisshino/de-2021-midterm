from fighter_scraper import scraper
import boto3


s3 = boto3.client('s3')
csv_path = scraper()
s3.upload_file(csv_path, 'data-engineer-bootcamp2-landing-zone-cs', f"fighter_output")