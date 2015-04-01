<?php

require_once "../../db/class.database.php";

$xml = simplexml_load_file('config.xml');

echo "Initializing $xml->name<br>";
echo "Version $xml->version<br>";

$db = new Database();
$dbh = $db->getDB();
$dbh->exec('CREATE TABLE IF NOT EXISTS `dropbox` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(255) DEFAULT NULL,
  `userid` varchar(255) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;');

system('mkdir -p /usr/share/JBOCD');
system('mv ./python/* /var/JBOCD/module/');
system('cd /usr/share/JBOCD && pip install --upgrade dropbox'); 

echo "Database updated!";
header("Location: http://".$_SERVER['SERVER_NAME']."/admin/?p=dropbox");
die();

?>