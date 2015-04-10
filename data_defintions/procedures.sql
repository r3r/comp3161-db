use compustore_online;
-- Function to get order total given an order
DELIMITER $$
CREATE FUNCTION getOrderTotal(order_id int(11)) RETURNS float READS SQL DATA
  BEGIN
     DECLARE total float;
     SET total = 0;
     SELECT COALESCE(sum(line_total),0) INTO total  FROM line_item
     WHERE orderid=order_id;
     return (total);
  END $$
DELIMITER ;


-- Procedure to get all customer totals over a defined date period.
DELIMITER $$
CREATE PROCEDURE getCustomerTotalsDate(IN start_date date, IN end_date date)
   BEGIN
       SELECT cust.*, grand_total
          FROM (
              SELECT sum(total) as grand_total, custid
              FROM (
                  SELECT getOrderTotal(orderid) as total, orderid, custid
                  FROM online_purchases as op
                  WHERE purchase_date BETWEEN start_date AND end_date) as a
              GROUP BY custid ) as b, customer as cust
       WHERE b.custid = cust.custid
       ORDER BY grand_total DESC;
   END $$
DELIMITER ;

-- Procedure to get all customer totals over a defined threshold.
DELIMITER $$
CREATE PROCEDURE getCustomerTotalsThreshold(IN amount float)
   BEGIN
       SELECT cust.*, grand_total
          FROM (
              SELECT sum(total) as grand_total, custid
              FROM (
                  SELECT getOrderTotal(orderid) as total, orderid, custid
                  FROM online_purchases as op) as a
              GROUP BY custid ) as b, customer as cust
       WHERE b.custid = cust.custid AND grand_total >= amount
       ORDER BY grand_total DESC;
   END $$
DELIMITER ;



-- Procedure to get top sales in a branch
use compustore_branch1;
DELIMITER $$
CREATE PROCEDURE getLaptopsByTopSale()
    BEGIN
        SELECT * FROM
            (SELECT vendor, model, sum(quantity) as num_sales FROM
                line_item GROUP BY vendor, model) as z
         ORDER BY num_sales DESC;
    END $$
DELIMITER ;
-- Funciton to calculate number of sales
DELIMITER $$
CREATE FUNCTION getNumberOfSales(start_date date, end_date date) RETURNS int READS SQL DATA
  BEGIN
     DECLARE total int;
     SET total = 0;
     SELECT count(*) INTO total  FROM store_purchases
     WHERE purchase_date BETWEEN start_date AND end_date;
     return (total);
  END $$
DELIMITER ;
-- Procedure to get top sales in a branch
use compustore_branch2;
DELIMITER $$
CREATE PROCEDURE getLaptopsByTopSale()
    BEGIN
        SELECT * FROM
            (SELECT vendor, model, sum(quantity) as num_sales FROM
                line_item GROUP BY vendor, model) as z
         ORDER BY num_sales DESC;
    END $$
DELIMITER ;
-- Funciton to calculate number of sales
DELIMITER $$
CREATE FUNCTION getNumberOfSales(start_date date, end_date date) RETURNS int READS SQL DATA
  BEGIN
     DECLARE total int;
     SET total = 0;
     SELECT count(*) INTO total  FROM store_purchases
     WHERE purchase_date BETWEEN start_date AND end_date;
     return (total);
  END $$
DELIMITER ;
-- Procedure to get top sales in a branch
use compustore_branch3;
DELIMITER $$
CREATE PROCEDURE getLaptopsByTopSale()
    BEGIN
        SELECT * FROM
            (SELECT vendor, model, sum(quantity) as num_sales FROM
                line_item GROUP BY vendor, model) as z
         ORDER BY num_sales DESC;
    END $$
DELIMITER ;
-- Funciton to calculate number of sales
DELIMITER $$
CREATE FUNCTION getNumberOfSales(start_date date, end_date date) RETURNS int READS SQL DATA
  BEGIN
     DECLARE total int;
     SET total = 0;
     SELECT count(*) INTO total  FROM store_purchases
     WHERE purchase_date BETWEEN start_date AND end_date;
     return (total);
  END $$
DELIMITER ;