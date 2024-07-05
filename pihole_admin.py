#!/usr/bin/env python3

import argparse
import logging
import matplotlib.pyplot as plt
import os
import requests
import sqlite3
import sys
import time
import re
from collections import defaultdict
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
from tabulate import tabulate
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

class PiholeDBAdmin:
    def __init__(self, gravity_db_path: str = "/etc/pihole/gravity.db", query_db_path: str = "/etc/pihole/pihole-FTL.db"):
        self.gravity_db_path = gravity_db_path
        self.query_db_path = query_db_path
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("PiholeDBAdmin")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        return logger

    def _get_connection(self, db_path: str) -> sqlite3.Connection:
        return sqlite3.connect(db_path)

    def optimize_database(self) -> None:
        self.logger.info("Starting database optimization...")

        dbs = [self.gravity_db_path, self.query_db_path]
        summaries = []

        for db in dbs:
            with self._get_connection(db) as conn:
                cursor = conn.cursor()

                cursor.execute("PRAGMA page_count")
                initial_pages = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                initial_size = initial_pages * page_size / 1024 / 1024  # Size in MB

                cursor.execute("PRAGMA freelist_count")
                initial_fragmentation = cursor.fetchone()[0] * page_size / 1024 / 1024  # Fragmentation in MB

                start_time = time.time()
                conn.execute("VACUUM")
                vacuum_time = time.time() - start_time

                cursor.execute("PRAGMA page_count")
                post_vacuum_pages = cursor.fetchone()[0]
                post_vacuum_size = post_vacuum_pages * page_size / 1024 / 1024  # Size in MB

                cursor.execute("PRAGMA freelist_count")
                post_vacuum_fragmentation = cursor.fetchone()[0] * page_size / 1024 / 1024  # Fragmentation in MB

                start_time = time.time()
                conn.execute("ANALYZE")
                analyze_time = time.time() - start_time

                cursor.execute("SELECT COUNT(*) FROM sqlite_stat1")
                stats_count = cursor.fetchone()[0]

            summary = f"""
Database: {db}
Initial State:
  - Size: {initial_size:.2f} MB
  - Fragmentation: {initial_fragmentation:.2f} MB

VACUUM Operation:
  - Duration: {vacuum_time:.2f} seconds
  - Size after VACUUM: {post_vacuum_size:.2f} MB
  - Fragmentation after VACUUM: {post_vacuum_fragmentation:.2f} MB
  - Space saved: {initial_size - post_vacuum_size:.2f} MB

ANALYZE Operation:
  - Duration: {analyze_time:.2f} seconds
  - Table statistics gathered: {stats_count}

Final Results:
  - Total optimization time: {vacuum_time + analyze_time:.2f} seconds
  - Final database size: {post_vacuum_size:.2f} MB
  - Total space saved: {initial_size - post_vacuum_size:.2f} MB
  - Total fragmentation reduced: {initial_fragmentation - post_vacuum_fragmentation:.2f} MB

Changes Made:
  - Database size change: {post_vacuum_size - initial_size:+.2f} MB
  - Fragmentation change: {post_vacuum_fragmentation - initial_fragmentation:+.2f} MB
"""
            summaries.append(summary)

        print("\n".join(summaries))
        self.logger.info("Database optimization completed.")

    def backup_database(self, backup_path: str) -> None:
        self.logger.info(f"Backing up databases to {backup_path}")
        os.makedirs(backup_path, exist_ok=True)

        dbs = [self.gravity_db_path, self.query_db_path]
        for db in dbs:
            db_name = os.path.basename(db)
            backup_file = os.path.join(backup_path, f"{db_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")

            start_time = time.time()
            with self._get_connection(db) as conn:
                backup = sqlite3.connect(backup_file)
                conn.backup(backup)
                backup.close()
            backup_time = time.time() - start_time
            backup_size = os.path.getsize(backup_file) / 1024 / 1024  # Size in MB
            self.logger.info(f"Database {db_name} backup completed in {backup_time:.2f} seconds")
            self.logger.info(f"Backup size: {backup_size:.2f} MB")

    def get_statistics(self) -> Dict[str, Any]:
        self.logger.info("Fetching database statistics...")
        stats = {}
        stats['stats_generated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection(self.gravity_db_path) as conn:
            cursor = conn.cursor()

            def safe_execute(query, default=0):
                try:
                    cursor.execute(query)
                    return cursor.fetchone()[0]
                except sqlite3.OperationalError as e:
                    self.logger.warning(f"Query failed: {query}. Error: {str(e)}")
                    return default

            stats['total_domains'] = int(safe_execute("SELECT COUNT(*) FROM gravity"))
            stats['whitelisted_domains'] = int(safe_execute("SELECT COUNT(*) FROM domainlist WHERE type = 0 AND enabled = 1"))
            stats['blacklisted_domains'] = int(safe_execute("SELECT COUNT(*) FROM domainlist WHERE type = 1 AND enabled = 1"))
            stats['regex_whitelist'] = int(safe_execute("SELECT COUNT(*) FROM domainlist WHERE type = 2 AND enabled = 1"))
            stats['regex_blacklist'] = int(safe_execute("SELECT COUNT(*) FROM domainlist WHERE type = 3 AND enabled = 1"))
            stats['total_adlists'] = int(safe_execute("SELECT COUNT(*) FROM adlist WHERE enabled = 1"))
            stats['adlist_urls'] = int(safe_execute("SELECT COUNT(DISTINCT address) FROM adlist WHERE enabled = 1"))

            cursor.execute("SELECT value FROM info WHERE property = 'gravity_count'")
            result = cursor.fetchone()
            stats['gravity_count'] = int(result[0]) if result else 0

            cursor.execute("SELECT value FROM info WHERE property = 'updated'")
            result = cursor.fetchone()
            if result:
                last_updated = datetime.fromtimestamp(int(result[0]))
                stats['last_gravity_update'] = last_updated.strftime("%m-%d-%Y %I:%M:%S %p")
            else:
                stats['last_gravity_update'] = "Unknown"

        with self._get_connection(self.query_db_path) as conn:
            cursor = conn.cursor()

            stats['total_queries'] = int(safe_execute("SELECT COUNT(*) FROM queries"))
            stats['blocked_queries'] = int(safe_execute("SELECT COUNT(*) FROM queries WHERE status IN (1, 4, 5, 6, 7, 8, 9, 10, 11)"))
            stats['forwarded_queries'] = int(safe_execute("SELECT COUNT(*) FROM queries WHERE status = 2"))
            stats['cached_queries'] = int(safe_execute("SELECT COUNT(*) FROM queries WHERE status = 3"))

            if stats['total_queries'] > 0:
                stats['blocking_percentage'] = (stats['blocked_queries'] / stats['total_queries']) * 100
            else:
                stats['blocking_percentage'] = 0.0

        self.logger.info("Statistics fetched successfully.")
        return stats

    def clean_old_data(self, days: int = 30) -> None:
        self.logger.info(f"Cleaning data older than {days} days...")
        with self._get_connection(self.query_db_path) as conn:
            cursor = conn.cursor()
            timestamp = int((datetime.now() - timedelta(days=days)).timestamp())

            cursor.execute("SELECT COUNT(*) FROM query_storage WHERE timestamp < ?", (timestamp,))
            queries_to_delete = cursor.fetchone()[0]

            cursor.execute("DELETE FROM query_storage WHERE timestamp < ?", (timestamp,))
            conn.commit()

        self.logger.info(f"Deleted {queries_to_delete} old queries.")
        self.logger.info("Old data cleaned successfully.")

    def add_domains_to_list(self, domains: List[str], list_type: int) -> None:
        list_name = self.get_list_type(list_type)
        self.logger.info(f"Adding domains to {list_name}...")
        added_count = 0
        with self._get_connection(self.gravity_db_path) as conn:
            cursor = conn.cursor()
            for domain in domains:
                cursor.execute(
                    "INSERT OR IGNORE INTO domainlist (type, domain, enabled, date_added) VALUES (?, ?, 1, strftime('%s', 'now'))",
                    (list_type, domain)
                )
                if cursor.rowcount > 0:
                    added_count += 1
            conn.commit()
        self.logger.info(f"{added_count} domains added to {list_name} successfully.")

    def remove_domains_from_list(self, domains: List[str], list_type: int) -> None:
        list_name = self.get_list_type(list_type)
        self.logger.info(f"Removing domains from {list_name}...")
        removed_count = 0
        with self._get_connection(self.gravity_db_path) as conn:
            cursor = conn.cursor()
            for domain in domains:
                cursor.execute(
                    "DELETE FROM domainlist WHERE type = ? AND domain = ?",
                    (list_type, domain)
                )
                removed_count += cursor.rowcount
            conn.commit()
        self.logger.info(f"{removed_count} domains removed from {list_name} successfully.")

    def update_gravity(self) -> None:
        self.logger.info("Updating gravity...")
        start_time = time.time()
        result = os.system("pihole -g")
        update_time = time.time() - start_time
        if result == 0:
            self.logger.info(f"Gravity updated successfully in {update_time:.2f} seconds.")
        else:
            self.logger.error(f"Gravity update failed after {update_time:.2f} seconds.")

    def analyze_top_domains(self, limit: int = 10, blocked: bool = True) -> List[Dict[str, Any]]:
        self.logger.info(f"Analyzing top {limit} {'blocked' if blocked else 'allowed'} domains...")
        with self._get_connection(self.query_db_path) as conn:
            cursor = conn.cursor()
            if blocked:
                cursor.execute("""
                    SELECT domain, COUNT(*) as count
                    FROM queries
                    WHERE status IN (1, 4, 5, 6, 7, 8, 9, 10, 11)
                    GROUP BY domain
                    ORDER BY count DESC
                    LIMIT ?
                """, (limit,))
            else:
                cursor.execute("""
                    SELECT domain, COUNT(*) as count
                    FROM queries
                    WHERE status IN (2, 3)
                    GROUP BY domain
                    ORDER BY count DESC
                    LIMIT ?
                """, (limit,))
            results = [{"domain": row[0], "count": row[1]} for row in cursor.fetchall()]
        self.logger.info(f"Top {'blocked' if blocked else 'allowed'} domains analysis completed.")
        return results

    def run_custom_query(self, query: str) -> List[Dict[str, Any]]:
        self.logger.info("Running custom query...")
        with self._get_connection(self.query_db_path) as conn:
            cursor = conn.cursor()
            start_time = time.time()
            cursor.execute(query)
            query_time = time.time() - start_time
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        self.logger.info(f"Custom query executed successfully in {query_time:.2f} seconds.")
        return results

    def run_simplified_query(self, query_type: str, order_by: str, limit: int) -> List[Dict[str, Any]]:
        self.logger.info(f"Running simplified query: type={query_type}, order_by={order_by}, limit={limit}")
        with self._get_connection(self.query_db_path) as conn:
            cursor = conn.cursor()
            if query_type == 'domains':
                if order_by == 'blocked':
                    query = """
                    SELECT domain, COUNT(*) as total_queries, SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked_queries
                    FROM queries
                    GROUP BY domain
                    ORDER BY blocked_queries DESC
                    LIMIT ?
                    """
                else:  # default to ordering by total queries
                    query = """
                    SELECT domain, COUNT(*) as total_queries, SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked_queries
                    FROM queries
                    GROUP BY domain
                    ORDER BY total_queries DESC
                    LIMIT ?
                    """
            elif query_type == 'clients':
                if order_by == 'blocked':
                    query = """
                    SELECT client, COUNT(*) as total_queries, SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked_queries
                    FROM queries
                    GROUP BY client
                    ORDER BY blocked_queries DESC
                    LIMIT ?
                    """
                else:  # default to ordering by total queries
                    query = """
                    SELECT client, COUNT(*) as total_queries, SUM(CASE WHEN status IN (1,4,5,6,7,8,9,10,11) THEN 1 ELSE 0 END) as blocked_queries
                    FROM queries
                    GROUP BY client
                    ORDER BY total_queries DESC
                    LIMIT ?
                    """
            else:
                raise ValueError(f"Unknown query type: {query_type}")

            cursor.execute(query, (limit,))
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        self.logger.info("Simplified query executed successfully.")
        return results

    def generate_report(self) -> str:
        self.logger.info("Generating comprehensive report...")

        stats = self.get_statistics()
        top_blocked_domains = self.analyze_top_domains(10, blocked=True)
        top_allowed_domains = self.analyze_top_domains(10, blocked=False)

        report = []
        report.append("\nPi-hole Database Report")
        report.append("=======================\n")
        report.append("General Statistics:\n")
        report.append(f"Total domains in gravity: {stats['total_domains']:,}")
        report.append(f"Whitelisted domains: {stats['whitelisted_domains']:,}")
        report.append(f"Blacklisted domains: {stats['blacklisted_domains']:,}")
        report.append(f"Regex whitelist entries: {stats['regex_whitelist']:,}")
        report.append(f"Regex blacklist entries: {stats['regex_blacklist']:,}")
        report.append(f"Total enabled adlists: {stats['total_adlists']:,}")
        report.append(f"Unique adlist URLs: {stats['adlist_urls']:,}")
        report.append(f"Gravity count: {stats['gravity_count']:,}")
        report.append(f"Last gravity update: {stats['last_gravity_update']}")
        report.append(f"Total queries: {stats['total_queries']:,}")
        report.append(f"Blocked queries: {stats['blocked_queries']:,}")
        report.append(f"Forwarded queries: {stats['forwarded_queries']:,}")
        report.append(f"Cached queries: {stats['cached_queries']:,}")
        report.append(f"Blocking percentage: {stats['blocking_percentage']:.2f}%\n")

        report.append("Top 10 Blocked Domains:\n")
        report.append(tabulate(top_blocked_domains, headers="keys", tablefmt="grid"))
        report.append("\nTop 10 Allowed Domains:\n")
        report.append(tabulate(top_allowed_domains, headers="keys", tablefmt="grid"))

        report_str = "\n".join(report)
        print(report_str)

        self.generate_charts(top_blocked_domains, top_allowed_domains)

        return report_str

    def generate_charts(self, top_blocked_domains, top_allowed_domains):
        plt.figure(figsize=(12, 6))
        plt.subplot(121)
        plt.bar([d['domain'] for d in top_blocked_domains], [d['count'] for d in top_blocked_domains])
        plt.title('Top 10 Blocked Domains')
        plt.xlabel('Domain')
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha='right')

        plt.subplot(122)
        plt.bar([d['domain'] for d in top_allowed_domains], [d['count'] for d in top_allowed_domains])
        plt.title('Top 10 Allowed Domains')
        plt.xlabel('Domain')
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        plt.savefig('pihole_domain_stats.png')
        plt.close()
        self.logger.info("Charts saved as pihole_domain_stats.png")

    def check_for_updates(self) -> None:
        self.logger.info("Checking for Pi-hole updates...")
        try:
            result = os.popen("pihole -v").read()
            self.logger.info(f"Raw version output: {result}")
            current_version = result.split("Pi-hole version is ")[1].split("\n")[0].split()[0].strip()
            self.logger.info(f"Extracted current version: {current_version}")

            response = requests.get("https://api.github.com/repos/pi-hole/pi-hole/releases/latest")
            latest_version = response.json()["tag_name"].strip()
            self.logger.info(f"Extracted latest version: {latest_version}")

            if current_version != latest_version:
                self.logger.info(f"Update available: {latest_version} (current: {current_version})")
                user_input = input("\nDo you want to update Pi-hole? (y/n): ").lower().strip()
                if user_input == 'y':
                    self.update_pihole()
                else:
                    print("Update skipped.")
            else:
                self.logger.info("Pi-hole is up to date.")
        except Exception as e:
            self.logger.error(f"Error checking for updates: {str(e)}")

    def update_pihole(self) -> None:
        self.logger.info("Updating Pi-hole...")
        try:
            result = os.system("pihole -up")
            if result == 0:
                self.logger.info("Pi-hole updated successfully.")
                print("Pi-hole has been successfully updated.")
            else:
                self.logger.error("Pi-hole update failed.")
                print("Failed to update Pi-hole. Please check the logs for more information.")
        except Exception as e:
            self.logger.error(f"Error during Pi-hole update: {str(e)}")
            print(f"An error occurred during the update process: {str(e)}")

    def remove_duplicate_domains(self):
        self.logger.info("Searching for duplicate domains...")
        with self._get_connection(self.gravity_db_path) as conn:
            cursor = conn.cursor()

            # Get all domains from domainlist
            cursor.execute("SELECT id, domain, type FROM domainlist")
            all_domains = cursor.fetchall()

            # Create a dictionary to store unique domains
            unique_domains = {}
            duplicates = defaultdict(list)

            for id, domain, type in all_domains:
                normalized_domain = self.normalize_domain(domain)
                list_type = self.get_list_type(type)

                if normalized_domain in unique_domains:
                    existing_id, existing_domain, existing_list_type = unique_domains[normalized_domain]
                    duplicates[(existing_id, existing_domain, existing_list_type)].append((id, domain, list_type))
                else:
                    unique_domains[normalized_domain] = (id, domain, list_type)

        duplicate_groups = []
        for original, dup_list in duplicates.items():
            group = [original] + dup_list
            duplicate_groups.append(group)

        total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
        self.logger.info(f"Found {total_duplicates} duplicate entries.")
        return duplicate_groups

    @staticmethod
    def normalize_domain(domain):
        return domain.lower().strip()

    @staticmethod
    def get_list_type(type_value):
        list_types = {
            0: "exact whitelist",
            1: "exact blacklist",
            2: "regex whitelist",
            3: "regex blacklist"
        }
        return list_types.get(type_value, f"unknown list type ({type_value})")

    def find_similar_domains(self, similarity_threshold: int) -> Dict[str, List[str]]:
        self.logger.info(f"Searching for similar domains with a threshold of {similarity_threshold}%...")
        with self._get_connection(self.gravity_db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT domain, type FROM domainlist")
            domains = cursor.fetchall()

            similar_domains = defaultdict(list)

            def compare_domains(i, j):
                domain1, type1 = domains[i]
                domain2, type2 = domains[j]
                similarity_ratio = fuzz.ratio(domain1, domain2)
                if similarity_ratio >= similarity_threshold:
                    return (domain1, domain2, type1, type2, similarity_ratio)
                return None

            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(compare_domains, i, j)
                           for i in range(len(domains))
                           for j in range(i + 1, len(domains))]

                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        domain1, domain2, type1, type2, similarity_ratio = result
                        similar_domains[domain1].append((domain2, type2, similarity_ratio))
                        similar_domains[domain2].append((domain1, type1, similarity_ratio))

        self.logger.info(f"Found {len(similar_domains)} domains with similar matches.")
        return similar_domains

    @staticmethod
    def get_list_type(type_value):
        list_types = {
            0: "exact whitelist",
            1: "exact blacklist",
            2: "regex whitelist",
            3: "regex blacklist"
        }
        return list_types.get(type_value, "unknown list type")

    @staticmethod
    def get_list_type_value(list_type):
        list_type_values = {
            "exact whitelist": 0,
            "exact blacklist": 1,
            "regex whitelist": 2,
            "regex blacklist": 3
        }
        return list_type_values.get(list_type, -1)

    @staticmethod
    def normalize_domain(domain):
        domain = domain.lower()
        domain = re.sub(r'^(https?://)?(www\.)?', '', domain)
        domain = re.sub(r'/$', '', domain)
        return domain

def main():
    script_name = os.path.basename(sys.argv[0])

    examples = f"""
Examples:
  {script_name} --stats
  {script_name} --optimize
  {script_name} --backup /path/to/backup/folder
  {script_name} --clean 30
  {script_name} --add-whitelist "example.com another-example.com"
  {script_name} --remove-blacklist "badsite.com malware.org"
  {script_name} --update-gravity
  {script_name} --top-domains 20
  {script_name} --query domains --limit 10
  {script_name} --query clients --order-by queries --limit 5
  {script_name} --advanced-query "SELECT domain, COUNT(*) as count FROM queries GROUP BY domain ORDER BY count DESC LIMIT 10"
  {script_name} --report
  {script_name} --check-updates
  {script_name} --remove-duplicates
  {script_name} --find-similar 90
    """

    parser = argparse.ArgumentParser(description="Pi-hole Database Administrator",
                                     epilog=examples,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--optimize", "-o", action="store_true", help="Optimize the database")
    parser.add_argument("--backup", "-b", metavar="PATH", help="Backup the database to the specified path")
    parser.add_argument("--stats", "-s", action="store_true", help="Get database statistics")
    parser.add_argument("--clean", "-c", type=int, metavar="DAYS", help="Clean data older than specified days")
    parser.add_argument("--add-whitelist", "-aw", type=str, help="Add domains to whitelist (space-separated, enclose in quotes)")
    parser.add_argument("--add-blacklist", "-ab", type=str, help="Add domains to blacklist (space-separated, enclose in quotes)")
    parser.add_argument("--remove-whitelist", "-rw", type=str, help="Remove domains from whitelist (space-separated, enclose in quotes)")
    parser.add_argument("--remove-blacklist", "-rb", type=str, help="Remove domains from blacklist (space-separated, enclose in quotes)")
    parser.add_argument("--update-gravity", "-ug", action="store_true", help="Update gravity")
    parser.add_argument("--top-domains", "-td", type=int, metavar="LIMIT", help="Analyze top domains")
    parser.add_argument("--query", "-q", nargs="+", help="Run a simplified query on the Pi-hole database. Usage: --query <type> [--order-by <field>] [--limit <number>]. Types: domains, clients")
    parser.add_argument("--order-by", choices=['queries', 'blocked'], help="Order results by total queries or blocked queries")
    parser.add_argument("--limit", type=int, default=10, help="Limit the number of results (default: 10)")
    parser.add_argument("--advanced-query", "-aq", metavar="QUERY", help="Run an advanced SQL query on the Pi-hole database")
    parser.add_argument("--report", "-r", action="store_true", help="Generate a comprehensive report")
    parser.add_argument("--check-updates", "-u", action="store_true", help="Check for Pi-hole updates")
    parser.add_argument("--remove-duplicates", "-rd", action="store_true", help="Remove duplicate domains across all lists")
    parser.add_argument("--find-similar", "-fs", type=int, metavar="THRESHOLD", help="Find similar domains based on the specified similarity threshold (e.g., 90 for 90% similarity)")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    admin = PiholeDBAdmin()

    if args.optimize:
        admin.optimize_database()

    if args.backup:
        admin.backup_database(args.backup)

    if args.stats:
        stats = admin.get_statistics()
        print("\nPi-hole Database Statistics:")
        print("============================")
        print(f"Generated on: {stats['stats_generated_at']}\n")

        categories = {
            "Domains": ["total_domains", "whitelisted_domains", "blacklisted_domains", "regex_whitelist", "regex_blacklist"],
            "Adlists": ["total_adlists", "adlist_urls"],
            "Gravity": ["gravity_count", "last_gravity_update"],
            "Queries": ["total_queries", "blocked_queries", "forwarded_queries", "cached_queries", "blocking_percentage"]
        }

        for category, keys in categories.items():
            print(f"\n{category}:")
            print("-" * (len(category) + 1))
            for key in keys:
                if key in stats:
                    formatted_key = key.replace('_', ' ').title()
                    value = stats[key]
                    if isinstance(value, (int, float)):
                        if key == "blocking_percentage":
                            print(f"  {formatted_key}: {value:.2f}%")
                        else:
                            print(f"  {formatted_key}: {value:,}")
                    else:
                        print(f"  {formatted_key}: {value}")

        print("\nNote: All counts are current as of the last database update.")

    if args.clean:
        admin.clean_old_data(args.clean)

    if args.add_whitelist:
        domains = args.add_whitelist.split()
        admin.add_domains_to_list(domains, 0)

    if args.add_blacklist:
        domains = args.add_blacklist.split()
        admin.add_domains_to_list(domains, 1)

    if args.remove_whitelist:
        domains = args.remove_whitelist.split()
        admin.remove_domains_from_list(domains, 0)

    if args.remove_blacklist:
        domains = args.remove_blacklist.split()
        admin.remove_domains_from_list(domains, 1)

    if args.update_gravity:
        admin.update_gravity()

    if args.top_domains:
        top_blocked = admin.analyze_top_domains(args.top_domains, blocked=True)
        top_allowed = admin.analyze_top_domains(args.top_domains, blocked=False)
        print("\nTop Blocked Domains:")
        print(tabulate(top_blocked, headers="keys", tablefmt="grid"))
        print("\nTop Allowed Domains:")
        print(tabulate(top_allowed, headers="keys", tablefmt="grid"))

    if args.query:
        query_type = args.query[0]
        order_by = args.order_by or 'queries'
        limit = args.limit

        if query_type in ['domains', 'clients']:
            results = admin.run_simplified_query(query_type, order_by, limit)
            print(f"\nTop {limit} {query_type} (ordered by {order_by}):")
            print(tabulate(results, headers="keys", tablefmt="grid"))
        else:
            print(f"Unknown query type: {query_type}")
            sys.exit(1)

    if args.advanced_query:
        results = admin.run_custom_query(args.advanced_query)
        print("\nAdvanced Query Results:")
        print(tabulate(results, headers="keys", tablefmt="grid"))

    if args.report:
        admin.generate_report()

    if args.check_updates:
        admin.check_for_updates()

    if args.remove_duplicates:
        duplicate_groups = admin.remove_duplicate_domains()
        if duplicate_groups:
            print("\nFound Duplicate Domain Groups:")
            for i, group in enumerate(duplicate_groups, start=1):
                print(f"\nGroup {i}:")
                for id, domain, list_type in group:
                    print(f"  {domain} (ID: {id}, Type: {list_type})")

            create_log = input("\nDo you want to create an output log file with these results? (y/n): ").lower().strip()
            if create_log == 'y':
                script_dir = os.path.dirname(os.path.realpath(__file__))
                log_file_path = os.path.join(script_dir, 'duplicate-domains.txt')
                with open(log_file_path, 'w') as log_file:
                    log_file.write("Found Duplicate Domain Groups:\n")
                    for i, group in enumerate(duplicate_groups, start=1):
                        log_file.write(f"\nGroup {i}:\n")
                        for id, domain, list_type in group:
                            log_file.write(f"  {domain} (ID: {id}, Type: {list_type})\n")
                print(f"Log file created at: {log_file_path}")
        else:
            print("No duplicate domains found.")

    if args.find_similar:
        similar_domains = admin.find_similar_domains(args.find_similar)
        print("\nSimilar Domains:")
        for domain, matches in similar_domains.items():
            print(f"\nDomain: {domain}")
            print("Similar Matches:")
            for match in matches:
                print(f"  - {match[0]} (Type: {admin.get_list_type(match[1])}, Similarity: {match[2]}%)")

if __name__ == "__main__":
    main()
