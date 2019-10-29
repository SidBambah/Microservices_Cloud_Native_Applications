DROP TABLE if exists `profiles`;

CREATE TABLE `profiles` (
  `auto_id` mediumint(8) unsigned NOT NULL auto_increment,
  `id` varchar(36) NOT NULL unique,
  `last_name` varchar(255) default NULL,
  `first_name` varchar(255) default NULL,
  `email` varchar(255) default NULL unique,
  `status` varchar(255) default NULL,
  `password` varchar(255),
  PRIMARY KEY (`auto_id`)
) AUTO_INCREMENT=1;