from .connection import db


def get_paid_orders_for_client(client_id):
    try:
        with db.get_cursor(as_dict=True) as cursor:
            cursor.execute(
                """
                SELECT
                    o.id AS id,
                    o.created_at AS created_at,
                    c.vin AS vin,
                    b.name AS brand,
                    m.name AS model,
                    col.name AS color,
                    p.amount AS amount,
                    d.date AS delivery_date
                FROM car_order o
                JOIN car c ON c.id = o.car_id
                JOIN model m ON m.id = c.model_id
                JOIN brand b ON b.id = m.brand_id
                JOIN color col ON col.id = c.color_id
                JOIN LATERAL (
                    SELECT amount, datetime
                    FROM payment
                    WHERE order_id = o.id
                    AND status = 'success'
                    ORDER BY datetime DESC, id DESC
                    LIMIT 1
                ) p ON TRUE
                LEFT JOIN delivery d ON d.order_id = o.id
                WHERE o.client_id = %s
                AND o.status = 'completed'
                ORDER BY o.created_at DESC, o.id DESC;
                """,
                (client_id,),
            )
            rows = cursor.fetchall()

            for row in rows:
                row["car_name"] = f"{row['brand']} {row['model']}"
                row["date_formatted"] = row["created_at"].strftime("%Y-%m-%d %H:%M")
                row["amount_formatted"] = f"{int(row['amount']):,}".replace(",", " ")

                if row["delivery_date"] is None:
                    row["delivery_status_label"] = "Ожидает доставки"
                    row["delivery_status_class"] = "pending-delivery"
                else:
                    row["delivery_status_label"] = "Доставлено"
                    row["delivery_status_class"] = "delivered"
                    row["delivery_date_formatted"] = row["delivery_date"].strftime(
                        "%Y-%m-%d"
                    )

            return rows, ""
    except Exception as e:
        return None, f"server error: {str(e)}"

