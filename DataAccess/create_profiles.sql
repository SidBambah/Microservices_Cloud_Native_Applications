DROP TABLE if exists `profiles`;

CREATE TABLE `profiles` (
  `element_id` mediumint(8) unsigned NOT NULL auto_increment,
  `userid` varchar(255) default NULL,
  `element_type` ENUM('EMAIL', 'ADDRESS', 'TELEPHONE', 'OTHER') default NULL,
  `element_subtype` ENUM('WORK', 'HOME', 'MOBILE', 'OTHER') default NULL,
  `element_value` varchar(255) unique,
  `profileid` varchar(255) default NULL,
  PRIMARY KEY (`element_id`)
) AUTO_INCREMENT=1;