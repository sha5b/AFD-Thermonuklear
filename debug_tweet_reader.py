import csv

# Debug the CSV structure
def debug_csv():
    with open('tweets.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print(f"Total rows: {len(rows)}")
    
    # Check pairing
    i = 0
    pairs = 0
    singles = 0
    
    while i < len(rows):
        print(f"Row {i}: {rows[i]['username']} - {rows[i]['date']} - {rows[i]['content'][:50]}...")
        
        if i + 1 < len(rows):
            print(f"Row {i+1}: {rows[i+1]['username']} - {rows[i+1]['date']} - {rows[i+1]['content'][:50]}...")
            
            if rows[i]['username'] == rows[i+1]['username'] and rows[i]['date'] == rows[i+1]['date']:
                print(f"  -> PAIRED")
                pairs += 1
                i += 2
            else:
                print(f"  -> SINGLE")
                singles += 1
                i += 1
        else:
            print(f"  -> SINGLE (last row)")
            singles += 1
            i += 1
        
        print()
    
    print(f"Total pairs: {pairs}")
    print(f"Total singles: {singles}")

if __name__ == "__main__":
    debug_csv()
