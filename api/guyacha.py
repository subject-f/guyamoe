from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from misc.models import Variable

ENGINE_VARIABLE_KEY = "engine"


def ceil_15_dt(dt):
    return dt + (datetime.min - dt) % timedelta(minutes=15)


def get_gacha_stats():
    engine_var = Variable.objects.get(key=ENGINE_VARIABLE_KEY)

    engine = create_engine(engine_var.value)
    sess = sessionmaker(bind=engine)

    with sess() as session:
        stats = session.execute(
            """
            select sum(user_inventory_table.quantity) as total_rolls, count(*), item_table.item_type, item_table.rarity, item_table.max_drops
            from user_inventory_table
                join item_table
                    on user_inventory_table.item_id=item_table.item_id
            group by item_table.item_type, item_table.rarity, item_table.max_drops
            order by item_table.item_type, item_table.rarity desc
        """
        ).fetchall()

        net_gc = session.execute(
            """
            select sum(transaction_log_table.gc_recv) - sum(transaction_log_table.gc_sent) as total_money, transaction_log_table.user_id, discord_user_table.user_name, discord_user_table.user_pfp
            from transaction_log_table
                join discord_user_table
                    on transaction_log_table.user_id=discord_user_table.user_id
            where transaction_log_table.transaction_type='gacha'
            group by transaction_log_table.user_id, discord_user_table.user_name, discord_user_table.user_pfp
            order by total_money desc
            """
        ).fetchall()

        timestamps = session.execute(
            """
            select transaction_log_table.timestamp
            from transaction_log_table
            where transaction_log_table.transaction_type='gacha'
            order by transaction_log_table.timestamp
            """
        ).fetchall()

        item_counts = defaultdict(list)
        for total_rolls, unique_users, item_type, rarity, remaining_drops in stats:
            item_counts[item_type].append(
                {
                    "rarity": rarity,
                    "unique_users": unique_users,
                    "total_rolls": total_rolls,
                    "remaining_drops": remaining_drops,
                }
            )

        net_gc = [[a, b, c, d] for a, b, c, d in net_gc]

        start = ceil_15_dt(datetime.utcfromtimestamp(int(timestamps[0][0])))
        end = ceil_15_dt(datetime.utcfromtimestamp(int(timestamps[-1][0]) + 900))
        intervals = [
            [i, 0] for i in range(int(start.timestamp()), int(end.timestamp()), 900)
        ]
        intervals_dict = {}
        for idx, interval in enumerate(intervals):
            intervals_dict[interval[0]] = idx
        for timestamp in timestamps:
            get_rounded_up_15th_min = ceil_15_dt(
                datetime.utcfromtimestamp(int(timestamp[0]))
            ).timestamp()
            intervals[intervals_dict[int(get_rounded_up_15th_min)]][1] += 1

    return {
        "roll_stats": item_counts,
        "net_gc_earned_leaderboards": net_gc,
        "roll_rates": intervals,
    }
