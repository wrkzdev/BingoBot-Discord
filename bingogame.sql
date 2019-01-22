CREATE TABLE `bingo_active_players` (
  `discord_id` varchar(32) CHARACTER SET ascii NOT NULL,
  `discord_name` varchar(64) DEFAULT NULL,
  `started` varchar(32) CHARACTER SET ascii NOT NULL,
  `board_json` varchar(512) CHARACTER SET ascii NOT NULL,
  `board_jsonStar` varchar(512) CHARACTER SET ascii NOT NULL,
  `kicked` enum('NO','YES') NOT NULL DEFAULT 'NO',
  `kicked_when` varchar(32) CHARACTER SET ascii DEFAULT NULL,
  `lastSyncBlock` bigint(20) DEFAULT NULL,
  `gameID` int(11) DEFAULT NULL,
  KEY `discord_id` (`discord_id`),
  KEY `kicked` (`kicked`),
  KEY `lastSyncBlock` (`lastSyncBlock`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `bingo_active_players_archive` (
  `discord_id` varchar(32) CHARACTER SET ascii NOT NULL,
  `discord_name` varchar(64) DEFAULT NULL,
  `started` varchar(32) CHARACTER SET ascii NOT NULL,
  `board_json` varchar(512) CHARACTER SET ascii NOT NULL,
  `board_jsonStar` varchar(512) CHARACTER SET ascii NOT NULL,
  `kicked` enum('NO','YES') NOT NULL DEFAULT 'NO',
  `kicked_when` varchar(32) CHARACTER SET ascii DEFAULT NULL,
  `lastSyncBlock` bigint(20) DEFAULT NULL,
  `gameID` int(11) DEFAULT NULL,
  KEY `discord_id` (`discord_id`),
  KEY `gameID` (`gameID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `bingo_gamelist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `startedBlock` bigint(20) NOT NULL,
  `status` enum('COMPLETED','OPENED','SUSPENDED','ONGOING') NOT NULL DEFAULT 'OPENED',
  `gameType` enum('FOUR CORNERS','LINE','DIAGONALS','FULL HOUSE','ANY') NOT NULL DEFAULT 'ANY',
  `completed_when` varchar(32) DEFAULT NULL,
  `winner_id` varchar(32) DEFAULT NULL,
  `winner_name` varchar(64) DEFAULT NULL,
  `claim_Atheight` bigint(20) DEFAULT NULL,
  `reward` int(11) DEFAULT '20000',
  `rewardTx` varchar(64) DEFAULT NULL,
  `rewardNotWin` int(11) DEFAULT '1000',
  `rewardNotWinTx` varchar(64) DEFAULT NULL,
  `creator_discord_id` varchar(32) DEFAULT NULL,
  `creator_discord_name` varchar(64) DEFAULT NULL,
  `created_when` varchar(32) DEFAULT NULL,
  `remark` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `bingo_reminder` (
  `discord_id` varchar(32) NOT NULL,
  `discord_name` varchar(64) NOT NULL,
  KEY `discord_id` (`discord_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
