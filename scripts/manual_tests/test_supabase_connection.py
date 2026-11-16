from src.edurag_x.storage.supabase_client import get_supabase_client

try:
    client = get_supabase_client()
    response = client.storage.list_buckets()

    print("Supabase Connected Successfully!")
    print("Available Buckets:")

    for bucket in response:
        print("-", bucket.name)

except Exception as error:
    print("Supabase Connection Failed:")
    print(error)
