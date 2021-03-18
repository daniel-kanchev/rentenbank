from itemadapter import ItemAdapter
import sqlite3


class DatabasePipeline:
    # Database setup
    conn = sqlite3.connect('rentenbank.db')
    c = conn.cursor()

    def open_spider(self, spider):
        self.c.execute(""" CREATE TABLE IF NOT EXISTS articles (
        title text, 
        date text, 
        link text, 
        content text
        ) """)

    def process_item(self, item, spider):
        if 'date' in item.keys():
            self.c.execute("""SELECT * FROM articles WHERE title = ? AND date = ?""",
                           (item.get('title'), item.get('date')))
        else:
            self.c.execute("""SELECT * FROM articles WHERE title = ?""",
                           (item.get('title'), ))
        duplicate = self.c.fetchall()
        if len(duplicate):
            return item

        if 'link' in item.keys():
            print(f"New Article: {item['link']}")
        else:
            print(f"New Article: {item['title']}")

        # Insert values
        self.c.execute("INSERT INTO articles ("
                       "title, "
                       "date, "
                       "link, "
                       "content)"
                       " VALUES (?,?,?,?)",
                       (item.get('title'),
                        item.get('date'),
                        item.get('link'),
                        item.get('content')
                        ))
        self.conn.commit()  # commit after every entry

        return item

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()
