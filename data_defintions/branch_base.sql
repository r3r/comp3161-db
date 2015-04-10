CREATE TABLE inventory (
  quantity int(11) DEFAULT NULL,
  vendor varchar(25) NOT NULL,
  model varchar(25) NOT NULL,
  price decimal(8,2) DEFAULT NULL,
  ram int(11) DEFAULT NULL,
  hdd int(11) DEFAULT NULL,
  screensize float DEFAULT NULL,
  PRIMARY KEY (vendor,model)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

CREATE TABLE store_purchases (
  orderid int(11) NOT NULL,
  purchase_date date DEFAULT NULL,
  PRIMARY KEY (orderid)
) ENGINE=INNODB DEFAULT CHARSET=utf8;

CREATE TABLE line_item (
  vendor varchar(25) NOT NULL,
  model varchar(25) NOT NULL,
  orderid int(11) NOT NULL DEFAULT '0',
  quantity int(11) DEFAULT NULL,
  PRIMARY KEY (vendor,model,orderid),
  FOREIGN KEY (vendor, model) REFERENCES inventory(vendor, model) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (orderid) REFERENCES store_purchases(orderid) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=INNODB DEFAULT CHARSET=utf8;
CREATE INDEX purchase_date ON store_purchases (purchase_date);



