import csv

def remove_duplicates(read_file, out_file):
    lines = open(read_file).read().splitlines()
    writer = csv.writer(open(out_file, 'w'), delimiter=',')
    entries = set()
    for row in lines:
        if row not in entries:
            writer.writerow([row])
            entries.add(row)

if __name__ == '__main__':
    remove_duplicates('comment_pages_ratings_0901.csv', 'comment_pages_ratings_deduped.csv')
