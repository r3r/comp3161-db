create database compustore_online;
Use  compustore_online;
CREATE TABLE customer
  (
     custid     INT NOT NULL,
     first_name VARCHAR(255) NOT NULL,
     last_name VARCHAR(255) NOT NULL,
     address  VARCHAR (255) NOT NULL,
     phone    VARCHAR (10) NOT NULL,
     email    VARCHAR (25) NOT NULL,
     passwd VARCHAR (15) NOT NULL,
     PRIMARY KEY (custid)
  )
engine=innodb DEFAULT CHARSET=utf8;

CREATE TABLE creditcards
  (
     ccnumber     VARCHAR(16) NOT NULL,
     address      VARCHAR (255) NOT NULL,
     securitycode VARCHAR (20) NOT NULL,
     expirydate   DATE NOT NULL,
     custid       INT NOT NULL,
     PRIMARY KEY (ccnumber),
     FOREIGN KEY(custid) REFERENCES customer(custid)ON DELETE CASCADE ON UPDATE CASCADE
  )
engine=innodb DEFAULT CHARSET=utf8;

CREATE TABLE online_purchases
  (
     orderid       INT NOT NULL,
     purchase_date DATE NOT NULL,
     trackingno    TEXT(64) NOT NULL,
     custid        INT NOT NULL,
     PRIMARY KEY (orderid ),
     FOREIGN KEY (custid) REFERENCES customer (custid)ON DELETE CASCADE ON UPDATE CASCADE
  )
engine=innodb DEFAULT CHARSET=utf8;

-- Modified from the line_item in the ERD (to handle the distributed nature of the database)
CREATE TABLE line_item (
  vendor varchar(25) NOT NULL,
  model varchar(25) NOT NULL,
  branch_id varchar(25) NOT NULL,
  orderid int(11) NOT NULL,
  quantity int(11) NOT NULL
  line_total float NOT NULL ,
  PRIMARY KEY (vendor,model,orderid),
  FOREIGN KEY (orderid) REFERENCES online_purchases(orderid) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=INNODB DEFAULT CHARSET=utf8;

CREATE INDEX purchase_date ON online_purchases (purchase_date);