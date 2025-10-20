/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.3-MariaDB, for debian-linux-gnu (aarch64)
--
-- Host: db    Database: recipe_db
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `ingredients`
--

DROP TABLE IF EXISTS `ingredients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingredients` (
  `id` int NOT NULL AUTO_INCREMENT,
  `recipe_id` int DEFAULT NULL,
  `group_name` varchar(100) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `amount` varchar(100) NOT NULL,
  `is_optional` tinyint(1) DEFAULT NULL,
  `order_index` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `recipe_id` (`recipe_id`),
  KEY `ix_ingredients_id` (`id`),
  CONSTRAINT `ingredients_ibfk_1` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=779 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingredients`
--

LOCK TABLES `ingredients` WRITE;
/*!40000 ALTER TABLE `ingredients` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `ingredients` VALUES
(397,1,NULL,'wild rice','50g',0,0),
(398,1,NULL,'olive oil','2 tbsp',0,1),
(399,1,NULL,'boiling water','320g',0,2),
(400,1,NULL,'basmati rice','220g',0,3),
(401,1,NULL,'curry powder','2 tsp',0,4),
(402,1,NULL,'cooked chickpeas (drained)','240g',0,5),
(403,1,NULL,'medium onion, thinly sliced','1',0,6),
(404,1,NULL,'plain flour','1 ½ tbsp',0,7),
(405,1,NULL,'currants','100g',0,8),
(406,1,NULL,'chopped flat-leaf parsley','2 tbsp',0,9),
(407,1,NULL,'chopped coriander','1 tbsp',0,10),
(408,1,NULL,'chopped dill','1 tbsp',0,11),
(409,1,NULL,'salt and black pepper','',0,12),
(410,2,NULL,'light olive oil, plus extra for greasing','125ml',0,0),
(411,2,NULL,'demerara sugar','3 tbsp',0,1),
(412,2,NULL,'apricots, halved','8',0,2),
(413,2,NULL,'pistachio kernels','200g',0,3),
(414,2,NULL,'polenta','130g',0,4),
(415,2,NULL,'baking powder','1 tsp',0,5),
(416,2,NULL,'unwaxed lemon, zest','1',0,6),
(417,2,NULL,'fine sea salt','1/2 tsp',0,7),
(418,2,NULL,'medium free range eggs','3',0,8),
(419,2,NULL,'golden caster sugar','200g',0,9),
(420,2,NULL,'crème fraîche or greek yogurt, to serve (optional)','',0,10),
(421,3,'None','tablespoon olive oil','1',0,0),
(422,3,'None','shallots - peeled and diced','3',0,1),
(423,3,'None','arlic clove - crushed','2 g',0,2),
(424,3,'None','(1.33 lb) cauliflower - cut into florets','600 g',0,3),
(425,3,'None','(12.5 oz) potato - peeled and cut into 2cm chunks','350 g',0,4),
(426,3,'None','(1.5 oz) fresh ginger - grated','45 g',0,5),
(427,3,'None','tablespoon curry powder','3',0,6),
(428,3,'None','teaspoon chilli powder','1',0,7),
(429,3,'None','(14 oz) chopped tomatoes - canned','400 g',0,8),
(430,3,'None','vegetable stock pot','1',0,9),
(431,3,'None','(1 cups) boiling water','250 ml',0,10),
(432,3,'None','(0.85 cups) coconut milk','200 ml',0,11),
(433,3,'None','(0.33 cups) mango chutney','100 g',0,12),
(434,3,'None','fresh coriander (cilantro)','to taste',0,13),
(435,4,NULL,'de arroz (150 g)','2 tacitas',0,0),
(436,4,NULL,'de pollo troceados','2 muslos',0,1),
(437,4,NULL,'cebolla','1/2',0,2),
(438,4,NULL,'pimiento verde','1/2',0,3),
(439,4,NULL,'de ajo','1 diente',0,4),
(440,4,NULL,'de agua caliente o caldo','5 tacitas',0,5),
(441,4,NULL,'de aceite de oliva','3 cucharadas',0,6),
(442,4,NULL,'sal','',0,7),
(443,4,NULL,'de azafrán','hebras',0,8),
(444,4,NULL,'perejil picado','',0,9),
(445,5,NULL,'s all-purpose flour','2 cup',0,0),
(446,5,NULL,'salt','3/4 tsp',0,1),
(447,5,NULL,'warm water , plus 1 tbsp water','3/4 cup',0,2),
(448,5,NULL,'neutral oil','1 tsp',0,3),
(449,6,NULL,'potatoes','450 g',0,0),
(450,6,NULL,'unsalted butter','40 g',0,1),
(451,6,NULL,'all-purpose flour','30 g',0,2),
(452,6,NULL,'granulated sugar','20 g',0,3),
(453,6,NULL,'handful dried mushrooms e.g. porcini mushrooms','1',0,4),
(454,6,NULL,'heavy cream fat content about 30 %','180 ml',0,5),
(455,6,NULL,'tablespoon vinegar 5% acidity','3',0,6),
(456,6,NULL,'tablespoons fresh dill chopped, only leaves, no stems','3',0,7),
(457,6,NULL,'veg broth lukewarm, for soup','720 ml',0,8),
(458,6,NULL,'water to cook dried mushrooms','480 ml',0,9),
(459,6,NULL,'salt','',0,10),
(460,6,NULL,'teaspoon ground black pepper','0.25',0,11),
(461,6,NULL,'medium hard-boiled eggs','4',0,12),
(462,7,NULL,'oil','1 tbsp',0,0),
(463,7,NULL,'onion','1/2',0,1),
(464,7,NULL,'ginger','10g',0,2),
(465,7,NULL,'arlic cloves','2 g',0,3),
(466,7,NULL,'emon','l',0,4),
(467,7,NULL,'chick peas','1 can',0,5),
(468,7,NULL,'fennel seeds','1/2 tsp',0,6),
(469,7,NULL,'curry powder','1 tbsp',0,7),
(470,7,NULL,'tomatoes, chopped, or passata','3',0,8),
(471,7,NULL,'dates','3',0,9),
(472,7,NULL,'yougurt','',0,10),
(473,7,NULL,'coriander','',0,11),
(474,8,NULL,'onion','1',0,0),
(475,8,NULL,'arlic cloves','3 g',0,1),
(476,8,NULL,'carrot','1',0,2),
(477,8,NULL,'potato','1',0,3),
(478,8,NULL,'chicken stock','500ml',0,4),
(479,8,NULL,'honey','',0,5),
(480,8,NULL,'tomato paste','',0,6),
(481,8,NULL,'inger powder','g',0,7),
(482,8,NULL,'soy sauce','',0,8),
(483,8,NULL,'wostershire sauce','',0,9),
(484,8,NULL,'salt and pepper','',0,10),
(485,8,NULL,'curry powder','',0,11),
(486,8,NULL,'bay leaves','',0,12),
(487,9,NULL,'extra firm tofu pressed and chopped into 1/2 inch bite sized chunks','',0,0),
(488,9,NULL,'teaspoon salt','1',0,1),
(489,9,NULL,'tablespoons flour','2',0,2),
(490,9,NULL,'s garlic minced','7 clove',0,3),
(491,9,NULL,'red onion diced','1/4',0,4),
(492,9,NULL,'reen chilis or jalapenos, sliced','2 g',0,5),
(493,9,NULL,'whole scallions white parts chopped, green parts sliced on a bias','2',0,6),
(494,9,NULL,'teaspoon chili flakes','1',0,7),
(495,9,NULL,'tablespoon soy sauce','1',0,8),
(496,9,NULL,'tablespoon white wine vinegar','1',0,9),
(497,9,NULL,'tablespoons honey','2',0,10),
(498,9,NULL,'tablespoon mirin','1/2',0,11),
(499,9,NULL,'tablespoons vegetable oil','4',0,12),
(500,9,NULL,'tablespoon sesame oil','1/2',0,13),
(501,9,NULL,'tablespoon toasted sesame seeds','1',0,14),
(502,9,NULL,'noodles or rice','',0,15),
(503,10,NULL,'unsalted butter','30g',0,0),
(504,10,NULL,'onion, sliced','1',0,1),
(505,10,NULL,'arlic cloves, crushed','2 g',0,2),
(506,10,NULL,'zest and juice 3 lemons (ideally sicilian), plus wedges to serve','',0,3),
(507,10,NULL,'’nduja, crumbled','50g',0,4),
(508,10,NULL,'bunch fresh flatleaf parsley, chopped','',0,5),
(509,10,NULL,'extra-virgin olive oil, plus extra for frying','3 tbsp',0,6),
(510,10,NULL,'fresh white breadcrumbs','50g',0,7),
(511,10,NULL,'fresh pappardelle','400g',0,8),
(512,10,NULL,'parmesan, grated, plus extra to serve','40g',0,9),
(513,11,NULL,'eggs','3',0,0),
(514,11,NULL,'potato and a half (450gr)','1',0,1),
(515,11,NULL,'onion','1/2',0,2),
(516,11,NULL,'parsley and salt','',0,3),
(517,12,'None','butternut squash','1/2',0,0),
(518,12,'None','bulb garlic','1',0,1),
(519,12,'None','olive oil','to taste',0,2),
(520,12,'None','itre stock','1/2 l',0,3),
(521,12,'None','thyme','to taste',0,4),
(522,12,'None','salt','to taste',0,5),
(523,12,'None','pepper','to taste',0,6),
(524,13,NULL,'oil','30ml',0,0),
(525,13,NULL,'spring/purple onion','1',0,1),
(526,13,NULL,'raw cashews, roughly crushed or chopped','20g',0,2),
(527,13,NULL,'fresh ginger','5g',0,3),
(528,13,NULL,'white sesame seeds','1/2 tbsp',0,4),
(529,13,NULL,'soy sauce','25ml',0,5),
(530,13,NULL,'rice-wine vinegar','1/2 tbsp',0,6),
(531,13,NULL,'honey','1 tbsp',0,7),
(532,13,NULL,'paprika','1/2 tsp',0,8),
(533,13,NULL,'shichimi togarashi','1/2 tsp',0,9),
(534,13,NULL,'aubergine','1',0,10),
(535,13,NULL,'salt','1/2 tsp',0,11),
(536,14,NULL,'arge cauliflower, cut into bite-sized florets','1/2 l',0,0),
(537,14,NULL,'red onion, sliced into wedges','1/2',0,1),
(538,14,NULL,'groundnut oil','2 tbsp',0,2),
(539,14,NULL,'cornflour','1/2 tbsp',0,3),
(540,14,NULL,'cherry vinegar','1 tbsp',0,4),
(541,14,NULL,'+ 1/2 tbsp shaoxing rice wine','1',0,5),
(542,14,NULL,'soy sauce','2 tbsp',0,6),
(543,14,NULL,'pack fine egg noodles','125g',0,7),
(544,14,NULL,'s garlic, finely sliced','2 clove',0,8),
(545,14,NULL,'chilli flakes','1 tsp',0,9),
(546,14,NULL,'cashews','25g',0,10),
(547,15,NULL,'olive oil','2 tbsp',0,0),
(548,15,NULL,'s garlic, peeled and crushed','3 clove',0,1),
(549,15,NULL,'bay leaves','2',0,2),
(550,15,NULL,'coriander seeds, lightly crushed','1/2 tsp',0,3),
(551,15,NULL,'small chilli, thinly sliced','1',0,4),
(552,15,NULL,'eek (150 gr), halved and sliced','1 l',0,5),
(553,15,NULL,'salt','1 tsp',0,6),
(554,15,NULL,'cooking chorizo','200g',0,7),
(555,15,NULL,'-4 vine tomatoes (300 gr) finely chopped','3',0,8),
(556,15,NULL,'tomato puree','2 tbsp',0,9),
(557,15,NULL,'smoked paprika','1 tsp',0,10),
(558,15,NULL,'sweet paprika','1 tsp',0,11),
(559,15,NULL,'r paella rice','250 g',0,12),
(560,15,NULL,'fresh parsley, roughly chopped','',0,13),
(561,16,NULL,'rams self-raising flour','185 g',0,0),
(562,16,NULL,'rams cocoa powder','30 g',0,1),
(563,16,NULL,'rams unsalted butter (plus more to grease cake tin - i use the butter wrapper)','250 g',0,2),
(564,16,NULL,'tablespoon chambord (raspberry liqueur)','1',0,3),
(565,16,NULL,'rams caster sugar','95 g',0,4),
(566,16,NULL,'rams light brown muscovado sugar','95 g',0,5),
(567,16,NULL,'rams good dark chocolate - 70% cocoa solids (broken into squares)','250 g',0,6),
(568,16,NULL,'millilitres black coffee and 185ml / ¾ cup water or 2 teaspoons instant coffee made up with 370ml / 1½ cups water','185',0,7),
(569,16,NULL,'arge eggs at room temperature (beaten slightly)','2 l',0,8),
(570,16,NULL,'rams raspberries (plus lots more to serve)','250 g',0,9),
(571,16,NULL,'approx. ½ teaspoon icing sugar (to serve)','',0,10),
(572,17,NULL,'ripe bananas (peeled weight)','350g',0,0),
(573,17,NULL,'plain flour, plus extra for the tin','180g',0,1),
(574,17,NULL,'baking powder','2½ tsp',0,2),
(575,17,NULL,'salt','1 tsp',0,3),
(576,17,NULL,'sugar (i used 90 plus amaretto)','160g',0,4),
(577,17,NULL,'eggs, beaten','2',0,5),
(578,17,NULL,'melted butter, plus extra to grease, slightly cooled','4 tbsp',0,6),
(579,17,NULL,'walnuts, roughly chopped','50g',0,7),
(580,17,NULL,'extras like dates, figs, coconut on top','',0,8),
(581,18,NULL,'r flour, half wholemeal','110 g',0,0),
(582,18,NULL,'r brown sugar','50 g',0,1),
(583,18,NULL,'baking powder','1 tsp',0,2),
(584,18,NULL,'baking soda','1/8 tsp',0,3),
(585,18,NULL,'salt','1/8 tsp',0,4),
(586,18,NULL,'cinammon','1 tsp',0,5),
(587,18,NULL,'arge banana or 2 small','1 l',0,6),
(588,18,NULL,'r peanut butter','60 g',0,7),
(589,18,NULL,'oil','50 ml',0,8),
(590,18,NULL,'egg','1',0,9),
(591,18,NULL,'milk','40 ml',0,10),
(592,18,NULL,'vanilla','',0,11),
(593,18,NULL,'chocolate chips','3 tsp',0,12),
(594,19,NULL,'full-fat cream cheese, at room temperature','600g',0,0),
(595,19,NULL,'sugar','150g',0,1),
(596,19,NULL,'arge free-range eggs, at room temperature','3 l',0,2),
(597,19,NULL,'soured cream, at room temperature','300ml',0,3),
(598,19,NULL,'fine sea salt','¼ tsp',0,4),
(599,19,NULL,'cornflour','25g',0,5),
(600,20,NULL,'r flour','100g',0,0),
(601,20,NULL,'r sugar','125g',0,1),
(602,20,NULL,'r butter','125g',0,2),
(603,20,NULL,'r almond flour','25g',0,3),
(604,20,NULL,'satchet of yeast','1/2',0,4),
(605,20,NULL,'r cocoa powder','30g',0,5),
(606,20,NULL,'eggs','3',0,6),
(607,20,NULL,'teaspoon of baking powder','1',0,7),
(608,20,NULL,'pods of cardamom, crushed','5',0,8),
(609,21,NULL,'graham cracker crumbs','75g',0,0),
(610,21,NULL,'packed light brown sugar','25g',0,1),
(611,21,NULL,'unsalted butter, melted','30g',0,2),
(612,21,NULL,'one 400g can sweetened condensed milk','',0,3),
(613,21,NULL,'plain greek yogurt','120g',0,4),
(614,21,NULL,'grated lime zest','7g',0,5),
(615,21,NULL,'fresh lime juice','80ml',0,6),
(616,21,NULL,'cold heavy cream','120ml',0,7),
(617,21,NULL,'confectioners\' sugar','8g',0,8),
(618,21,NULL,'grated lime zest','2.5g',0,9),
(619,21,NULL,'to 5 thin lime slices','4',0,10),
(620,22,NULL,'arge egg','1 l',0,0),
(621,22,NULL,'granulated sugar','80g',0,1),
(622,22,NULL,'greek yogurt','80g',0,2),
(623,22,NULL,'vegetable oil','60ml',0,3),
(624,22,NULL,'ground cardamom','½ tsp',0,4),
(625,22,NULL,'rose water','1 tbsp',0,5),
(626,22,NULL,'all-purpose flour','110g',0,6),
(627,22,NULL,'cornstarch','12g',0,7),
(628,22,NULL,'baking powder','1 tsp',0,8),
(629,22,NULL,'toasted sesame seeds (optional)','1 tbsp',0,9),
(630,23,NULL,'de harina','290 g',0,0),
(631,23,NULL,'de leche','90 ml',0,1),
(632,23,NULL,'de azúcar','60 g',0,2),
(633,23,NULL,'huevo grandes','1',0,3),
(634,23,NULL,'de levadura seca','5 g',0,4),
(635,23,NULL,'de mantequilla','40 g',0,5),
(636,23,NULL,'ralladura de media naranja y un cuarto de limón','',0,6),
(637,23,NULL,'de agua de azahar','2 cucharadas',0,7),
(638,23,NULL,'de sal','1 pizca',0,8),
(639,23,NULL,'itro de nata con 35% de materia grasa','1/2 l',0,9),
(640,24,NULL,'(about 8 ounces) ricotta cheese','1 cup',0,0),
(641,24,NULL,'milk','3/4 cup',0,1),
(642,24,NULL,'eggs, separated','4',0,2),
(643,24,NULL,'teaspoon vanilla extract','1/2',0,3),
(644,24,NULL,'(about 5 ounces) all-purpose flour','1 cup',0,4),
(645,24,NULL,'teaspoon baking powder','1',0,5),
(646,24,NULL,'teaspoon salt','1/2',0,6),
(647,24,NULL,'tablespoon sugar','1',0,7),
(648,24,NULL,'teaspoon grated lemon zest','1',0,8),
(649,24,NULL,'teaspoons unsalted butter, plus more for serving','2',0,9),
(650,24,NULL,'fruit and/or syrup for serving','',0,10),
(651,25,NULL,'olive oil','',0,0),
(652,25,NULL,'onion','1/2',0,1),
(653,25,NULL,'garlic','2 clove',0,2),
(654,25,NULL,'red pepper','1',0,3),
(655,25,NULL,'half tin of diced tomato','',0,4),
(656,25,NULL,'tomato paste','',0,5),
(657,25,NULL,'chili powder to taste','',0,6),
(658,25,NULL,'cumin to taste','',0,7),
(659,25,NULL,'paprika to taste','',0,8),
(660,25,NULL,'pinch of sugar','',0,9),
(661,25,NULL,'salt and pepper','',0,10),
(662,25,NULL,'eggs','2',0,11),
(663,25,NULL,'parsley or cilantro','',0,12),
(664,26,NULL,'dry yeast or 20g of fresh yeast','6g',0,0),
(665,26,NULL,'cold water','200ml',0,1),
(666,26,NULL,'strong white bread flour','550g',0,2),
(667,26,NULL,'sugar','50g',0,3),
(668,26,NULL,'eggs','3',0,4),
(669,26,NULL,'olive oil','4 tbsp',0,5),
(670,26,NULL,'⁄2 tsp fine sea salt','11',0,6),
(671,26,NULL,'egg wash','',0,7),
(672,26,NULL,'grams raisins (optional)','1 cup',0,8),
(673,26,NULL,'fine sea salt','',0,9),
(674,27,NULL,'corn flour','3/4 cup',0,0),
(675,27,NULL,'gluten free flour','1/4 cup',0,1),
(676,27,NULL,'- 1/4 cup sugar','1/3',0,2),
(677,27,NULL,'salt','1/4 tsp',0,3),
(678,27,NULL,'baking powder','1/2 tbsp',0,4),
(679,27,NULL,'arge egg','1 l',0,5),
(680,27,NULL,'oil','1/4 cup',0,6),
(681,27,NULL,'+ 3 tbsp buttermilk (or milk)','1/2 cup',0,7),
(682,28,NULL,'strong white bread flour (plus a little extra for dusting)','500g',0,0),
(683,28,NULL,'cold water','330ml',0,1),
(684,28,NULL,'extra virgin olive oil (and a little extra for greasing)','50ml',0,2),
(685,28,NULL,'fine sea salt','2 tsp',0,3),
(686,28,NULL,'-5g dry yeast (activate it with part of the water and sugar) or 10g fresh yeast','4',0,4),
(687,28,NULL,'clear liquid honey','45g',0,5),
(688,28,NULL,'olive oil, for drizzling','',0,6),
(689,28,NULL,'sprigs of rosemary, needles only, chopped','2',0,7),
(690,28,NULL,'flaked sea salt, for sprinkling','',0,8),
(691,29,NULL,'r de bread flour','250 g',0,0),
(692,29,NULL,'r olive oil','75 g',0,1),
(693,29,NULL,'r dry yeast','5 g',0,2),
(694,29,NULL,'r lukewarm water','100 g',0,3),
(695,29,NULL,'r raisins','50 g',0,4),
(696,29,NULL,'r walnuts','50 g',0,5),
(697,29,NULL,'r sugar','10 g',0,6),
(698,29,NULL,'r aniseed','10 g',0,7),
(699,29,NULL,'salt','1/2 tsp',0,8),
(700,29,NULL,'r sesame seeds plus some extra for decoration','10 g',0,9),
(701,29,NULL,'one egg for decoration','',0,10),
(702,29,NULL,'sugar for decoration','',0,11),
(703,30,NULL,'spelt flour','450g',0,0),
(704,30,NULL,'yeast','10g',0,1),
(705,30,NULL,'honey','30g',0,2),
(706,30,NULL,'warm (23c) water','300ml',0,3),
(707,30,NULL,'salt','1 1/2 tsp',0,4),
(708,30,NULL,'ice cubes','',0,5),
(709,31,NULL,'milk','1l',0,0),
(710,31,NULL,'r sugar','200 g',0,1),
(711,31,NULL,'cinnamon stick','1',0,2),
(712,31,NULL,'emon rind','l',0,3),
(713,32,NULL,'r gram flour','120g',0,0),
(714,32,NULL,'water','320ml',0,1),
(715,32,NULL,'r olive oil','32g',0,2),
(716,32,NULL,'salt','1/2 tbsp',0,3),
(717,32,NULL,'rosemary','',0,4),
(718,33,NULL,'tomate 1 kg','',0,0),
(719,33,NULL,'pan 200 g','',0,1),
(720,33,NULL,'aceite de oliva virgen extra 150 ml','',0,2),
(721,33,NULL,'s de ajo 1','diente',0,3),
(722,33,NULL,'sal al gusto','',0,4),
(723,34,NULL,'yogurt','1/4 cup',0,0),
(724,34,NULL,'small egg','1',0,1),
(725,34,NULL,'olive oil','2 tbsp',0,2),
(726,34,NULL,'flour','1/2 cup',0,3),
(727,34,NULL,'small onion, finely chopped','1/2',0,4),
(728,34,NULL,'coriander','1 tbsp',0,5),
(729,34,NULL,'salt','1/4 tsp',0,6),
(730,34,NULL,'pepper','1/4 tsp',0,7),
(731,34,NULL,'chilli flakes','1/4 tsp',0,8),
(732,34,NULL,'baking soda','1/4 tsp',0,9),
(733,34,NULL,'baking powder','1/2 tsp',0,10),
(734,34,NULL,'cheese','1/4 cup',0,11),
(735,35,NULL,'yellow onion','1',0,0),
(736,35,NULL,'s garlic','4 clove',0,1),
(737,35,NULL,'s crushed tomatoes','2 can',0,2),
(738,35,NULL,'tomato paste to taste','1',0,3),
(739,35,NULL,'dried basil','1 tbsp',0,4),
(740,35,NULL,'dried oregano','1.5 tsp',0,5),
(741,35,NULL,'brown sugar','1 tbsp',0,6),
(742,35,NULL,'balsamic vinegar','1 tbsp',0,7),
(743,35,NULL,'olive oil','4 tbsp',0,8),
(744,35,NULL,'salt (or to taste)','1 tsp',0,9),
(745,36,NULL,'soft wheat 00 flour or plain flour 100g','',0,0),
(746,36,NULL,'chestnut flour 200g','',0,1),
(747,36,NULL,'dark soft brown sugar 100g','',0,2),
(748,36,NULL,'baking powder 1 tsp','',0,3),
(749,36,NULL,'salt ⅛ tsp','',0,4),
(750,36,NULL,'unsalted butter 130g, cold and diced','',0,5),
(751,36,NULL,'egg 50g (about 1 medium egg), at room temperature','',0,6),
(752,36,NULL,'dark chocolate chips 250g, or bar broken into small pieces (50-55% cocoa solids)','',0,7),
(753,37,NULL,'chickpea flour, sifted','1/4 cup',0,0),
(754,37,NULL,'water','1/2 cup',0,1),
(755,38,NULL,'chickpea + fava','3/4 cup',0,0),
(756,38,NULL,'onion','1/2',0,1),
(757,38,NULL,'arlic','3 g',0,2),
(758,38,NULL,'reen/purple onion','1/4 g',0,3),
(759,38,NULL,'parsley (no stems)','1/2 cup',0,4),
(760,38,NULL,'cilantro (no stems)','1/4 cup',0,5),
(761,38,NULL,'cumin','3 tsp',0,6),
(762,38,NULL,'chilli flakes','',0,7),
(763,38,NULL,'sesame seeds','',0,8),
(764,38,NULL,'salt','1/2 tbsp',0,9),
(765,38,NULL,'black pepper','1/4 tsp',0,10),
(766,38,NULL,'baking powder','1 tsp',0,11),
(767,39,NULL,'olive oil','40 ml',0,0),
(768,39,NULL,'r parmigiano reggiano','10 g',0,1),
(769,39,NULL,'tomato purée','1 tbsp',0,2),
(770,39,NULL,'oregano','2 tsp',0,3),
(771,39,NULL,'eggs','1',0,4),
(772,39,NULL,'salt','1/4 tsp',0,5),
(773,39,NULL,'r yogurt','50 g',0,6),
(774,39,NULL,'r feta','65 g',0,7),
(775,39,NULL,'r cherry tomatoes','40 g',0,8),
(776,39,NULL,'r flour','90 g',0,9),
(777,39,NULL,'baking powder','1/2 tsp',0,10),
(778,39,NULL,'bicarbonate of soda','1/2 tsp',0,11);
/*!40000 ALTER TABLE `ingredients` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `instructions`
--

DROP TABLE IF EXISTS `instructions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `instructions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `recipe_id` int DEFAULT NULL,
  `step_number` int NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `recipe_id` (`recipe_id`),
  KEY `ix_instructions_id` (`id`),
  CONSTRAINT `instructions_ibfk_1` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=486 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `instructions`
--

LOCK TABLES `instructions` WRITE;
/*!40000 ALTER TABLE `instructions` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `instructions` VALUES
(246,1,1,'Start by putting the wild rice in a small saucepan, cover with plenty of water, boil and leave to simmer for about 40 minutes. To cook the basmati rice, pour a tablespoon of oil into a large saucepan and gently fry 1 thinly sliced onion for 5 minutes until softened. Add the rice and ½ teaspoon of salt and stir for 1 minute. Carefully add the boiling water to reduce the heat. Put the lid on and leave to cook for 15 minutes. Remove the pan from the heat, cover with a clean tea towel and leave to cool for 10 minutes. While the rice is cooking, prepare the chickpeas. Heat the olive oil in a small saucepan and add the cumin seeds and curry powder. Stir for a minute until combined. Add the teaspoon of salt and black pepper, the chickpeas and ¼ teaspoon of turmeric. Fry for 2 minutes and then place into a large bowl. Wipe the saucepan clean, pour in the sunflower oil, place on a high heat. Make sure the oil is hot. Then take a small piece of onion, about the size of a small coin. Take the onion and gently fry until golden brown. Put this aside. Meanwhile transfer all the other ingredients into the bowl with the chickpeas. Fry for 2 minutes. Finally, add both types of rice to the chickpeas and herbs. Add salt, oil and stir to taste. Add salt and pepper.'),
(247,2,1,'1 Lightly grease and line the base and sides of a 23cm springform cake tin with oil and baking parchment. Scatter the demerara sugar over the base of the tin, then arrange the apricots cut-side down over the top. Set aside.'),
(248,2,2,'2 Preheat the oven to 180°C, gas mark 4, and put a large baking tray in to heat up. Put 175g pistachios in a small food processor and whizz until finely ground. Put in a large bowl with the polenta, baking powder, lemon zest and salt; mix well, then set aside. In a separate large bowl, use an electric hand mixer to whisk the eggs and caster sugar until light and thickened (4-5 minutes). While still whisking, very slowly trickle in the oil until fully incorporated. Fold in the pistachio and polenta mixture.'),
(249,2,3,'3 Spoon the batter into the cake tin over the apricots. Put the tin on the hot baking tray, then bake for 45-55 minutes until golden brown and a skewer inserted into the middle comes out almost clean. Check after 35 minutes and if the cake is taking on too much colour, cover and continue to bake until cooked. Leave to cool for 10 minutes in the tin, then carefully turn out onto a serving plate and cool completely (or enjoy while still warm). Roughly chop the remaining 25g pistachios and scatter over the top. Delicious with crème fraîche or thick Greek yogurt, if liked.'),
(250,3,1,'Heat 1 tablespoon Olive oil in a large pan. Add 3 Shallots, 2 Garlic clove and 45 g Fresh ginger. Cook on a very low heat for 5 minutes or until softened.'),
(251,3,2,'Add 3 tablespoon Curry powder and 1 teaspoon Chilli powder. Stir and cook for a further minute.'),
(252,3,3,'Add 400 g Chopped tomatoes, 350 g Potato, 600 g Cauliflower250 ml Boiling water and 1 Vegetable stock pot. Mix well and cover with a lid. Cook on a low heat for 25 minutes.'),
(253,3,4,'Stir in 200 ml Coconut milk and 100 g Mango chutney. Cook for a further 3 minutes.'),
(254,3,5,'Serve topped with Fresh coriander (cilantro).'),
(255,4,1,'Pela el diente de ajo, pícalo en láminas, después en tiras y finalmente en daditos. Pica la cebolla.'),
(256,4,2,'Limpia el pimiento, aplástalo con la mano, retírale el tallo y las pepitas, **córtalo en tiras y después en daditos**.'),
(257,4,3,'Pon **3 cucharadas de aceite** en una cazuela amplia y baja, agrega la verdura y **rehógala a fuego medio** durante 4 minutos. Agrega el pollo troceado y dóralo junto con las **verduras** durante otros 4 minutos. Añade el **arroz** y rehógalo todo junto durante 2 minutos.'),
(258,4,4,'Vierte el **agua**, 1/2 cucharadita de **sal** (a tu gusto) y unas hebras de azafrán. Cuece a fuego fuerte durante 3 minutos. Tapa la cazuela y deja cocer durante otros **15-17 minutos a fuego suave**. Apaga el fuego y deja **reposar** tapado durante 5 minutos.'),
(259,4,5,'Sirve y espolvorea con perejil picado.'),
(260,5,1,'Add in the flour and salt into a mixing bowl. Mix.'),
(261,5,2,'Create a well in the center of the bowl and pour in the warm water.'),
(262,5,3,'Use a wooden spoon or spatula to mix the flour and water. Once the dough starts to come together, add in 1 tsp of oil.'),
(263,5,4,'Use your hands to mix the bits of dough. You can also use a stand mixer if you have one. Knead together for several minutes. If the dough is a bit dry, add a splash of water.'),
(264,5,5,'Keep kneading until you have a smooth ball of dough.'),
(265,5,6,'Shape the dough into a ball, then place it in a bowl.'),
(266,5,7,'Cover it with a damp towel and let it rest for 30 minutes.  # Making the wrappers'),
(267,5,8,'Add some flour on your work surface. Take the dough out of the bowl and knead it a few times.'),
(268,5,9,'Punch hole in the middle of the dough and then create a donut shape. Slowly stretch.'),
(269,5,10,'Slice the dough into 8 pieces. Roll or shape each piece of dough into a ball. Cover the dough with a towel to prevent from drying while you work on one at a time.'),
(270,5,11,'To make a wrapper, press down on the ball of dough and lightly flatten it over the surface. Sprinkle a little flour on top and lightly coat your rolling pin with some flour as well.'),
(271,5,12,'While holding both ends of the rolling pin, roll out the dough by moving the pin forward and backward. Rotate the dough 90 degrees and repeat the movement.'),
(272,5,13,'Continue to roll out the dough until you have a wrapper that’s around 5-5 ½ inches in diameter. If you can’t make them into a perfectly round shape, that’s okay! Mine weren’t perfect but I was still able to properly fold these together. It really takes some time and practice to get a hang of making wrappers.'),
(273,5,14,'Place the rolled out wrappers on a tray and cover with a dry towel to prevent them from drying out. Roll out the rest of the dough.'),
(274,5,15,'Take a rolled out piece of wrapper and place around 1/3-1/2 cup of filling into the center.'),
(275,5,16,'Crease the edges and pinch with your fingers. Twist to seal and then carefully press it down to flatten. See video for a visual guide. Afterwards, place back the pancake on the tray and cover with a dry towel to prevent it from drying out. Repeat for the rest of the wrappers.  # Cooking the pancakes'),
(276,5,17,'Heat a pan (with a lid), add in 1 tbsp of oil (for every 2 pancakes). When hot, add in the pancakes and lightly press down. Leave to cook over medium heat for 4-5 minutes until it has a golden brown crust. Flip over and leave to cook for another 4-5 until golden brown.'),
(277,5,18,'Prepare the lid of your pan. Using the lid as protection, carefully pour 2 tbsp of water (1 tbsp for each pancake) into the pan and then immediately cover to prevent it from splashing due to the heat. (I had mixed results doing this, the pancake will be soggy)'),
(278,5,19,'Leave to cook in the steam, until the water has evaporated, around 5-6 minutes. Take out the pies and repeat this step for the remaining ones. Enjoy while hot! See storage tips in the notes below.'),
(279,6,1,'Place dried mushrooms in a pot with 2 cups of water and bring to a boil. Reduce the heat and simmer for 15 minutes, then set aside.'),
(280,6,2,'Make a roux to thicken the kulajda soup: In a thick-bottomed pot, melt unsalted butter over medium heat. Add all-purpose flour and stir for 1 minute, until it creates a bubbling mass.'),
(281,6,3,'Start adding vegetable broth in batches: begin with ½ cup, stirring well. Continue adding the broth in small increments, stirring thoroughly each time, until all the broth is incorporated. This method will help prevent lumps in the soup.'),
(282,6,4,'Add the mushroom broth to the soup, straining out the cooked mushrooms. Season with salt and stir. Bring to a boil, then reduce the heat to a minimum. Cover with a lid and let it cook for 10 minutes.'),
(283,6,5,'Meanwhile, peel the potatoes and cut them into ½-inch cubes. Add them to the soup along with the cooked mushrooms and cook for another 15 minutes, or until the potato cubes have softened.'),
(284,6,6,'Chop the fresh dill, using only the soft green leaves and avoiding the stems.'),
(285,6,7,'Remove the soup from the stove, then pour in the cream and stir. Add vinegar, sugar, ground pepper, and chopped dill. Do not cook any further. Mix everything together with a wooden spoon, and season to your liking with salt and/or sugar if necessary.'),
(286,6,8,'Let the kulajda soup sit for 5 minutes before serving.'),
(287,7,1,'Heat the oil and cook the onion, ginger and garlic for 5 minutes'),
(288,7,2,'Peel 2 strips of lemon and add to the pan along with the chick peas and fennel seeds. Cook for 5 minutes'),
(289,7,3,'Sitr in the curry, tomatoes and dates, cook for 5 minutes'),
(290,7,4,'Add 50-100ml of water (depending on the tomatoes used) and continue to simmer for 5-10 minutes, until thickened'),
(291,7,5,'Switch off the stove, squeeze in a little lemon juice and season to taste'),
(292,7,6,'Serve with a paratha, yougurt and coriander'),
(293,8,1,'Chop the veggies and cook together until the onions are soft'),
(294,8,2,'Add the tomato paste and the dry ingredients. Stir for a little bit'),
(295,8,3,'Add the stock and the rest of the ingredients and let it cook until the potatoes are soft and the sauce is thick'),
(296,9,1,'If you are eating it with noodles, prepare them. You can eat it with rice too.'),
(297,9,2,'To a large bowl, add a pinch of salt and 2 tablespoons of flour to tofu chunks. Gently toss the tofu to make sure they are all evenly coated. Set aside.'),
(298,9,3,'Prep your vegetables by mincing the garlic, dicing the onion, slicing the chilis, and chopping up the scallions.'),
(299,9,4,'Prepare the sauce by mixing together chili flakes, soy sauce, white wine vinegar, honey, mirin, and 1 teaspoon of corn starch. Set aside.'),
(300,9,5,'To a very large non-stick pan, add 4 tablespoons of vegetable oil over high heat. When oil is very hot, add coated tofu chunks in one layer, making sure they are not touching each other. If they touch, they will stick to one another.'),
(301,9,6,'Cook the tofu and flip them one by one, until they are brown on all sides (approximately 7 minutes). Remove the tofu chunks from the pan and set them aside on a cooling rack to drain the excess oil. Repeat with the remaining tofu.'),
(302,9,7,'When all of the tofu has been fried, in the same pan, add 1 tablespoon of oil. Then add the garlic, onions, chilis, and scallions and saute the vegetables until the garlic starts to brown.'),
(303,9,8,'Reduce the heat to medium-high and add the sauce, stirring it with a wooden spoon until it reduces down into a thick sauce (approximately 30 seconds). Turn off the heat.'),
(304,9,9,'Gently add back the fried tofu and stir everything together, so that the tofu chunks are evenly coated in your sauce.'),
(305,9,10,'Garnish the tofu with ½ tablespoon of sesame oil and 1 tablespoon of toasted sesame seeds. Serve immediately.'),
(306,10,1,'Heat the butter in a large pan over a low heat and fry the shallots for 15 minutes until soft. Add the garlic, lemon zest and juice, then cook for a minute. Add the ’nduja and half the parsley, then fry for 1-2 minutes.'),
(307,10,2,'In a small frying pan, heat a glug of olive oil, add the breadcrumbs and fry over a medium heat for 3-4 minutes until crisp. Set aside.'),
(308,10,3,'Cook the pappardelle in a pan of boiling salted water for 3-4 minutes until almost tender. Drain, reserving a cupful of the cooking water, then add the pasta to the ’nduja mixture. Set over a medium heat, then toss with a splash of the pasta water, the 3 tbsp olive oil and the 40g parmesan.'),
(309,10,4,'Season to taste, divide among bowls, sprinkle with the crunchy breadcrumbs and remaining parsley, then serve with lemon wedges and extra parmesan.'),
(310,11,1,'Make the poor potatoes, adding all the ingredients at the same time. Cut the potatoes in half lengthwise, and then slice each half'),
(311,11,2,'Season with salt and parsley'),
(312,11,3,'Beat the eggs with salt and milk, mix everything'),
(313,11,4,'Cook the omelette, low heat and covered with a lid'),
(314,12,1,'Pre-heat oven to 200°C.'),
(315,12,2,'Peel and deseed butternut squash and dice into 1\" pieces.'),
(316,12,3,'Put butternut squash on a baking sheet, sprinkle with salt and pour about a tablespoon of olive oil on it and move around with your hands to make sure all dice are well coated with oil. Then spread out evenly into one layer.'),
(317,12,4,'Peel off the paper-like outer layer of the garlic bulb, leaving intact the skins of the individual cloves and being careful to keep the bulb as a whole.'),
(318,12,5,'Cut the top part of the garlic in order to expose the upper part of every clove (see video).'),
(319,12,6,'Drizzle a few drops of olive oil onto each clove.'),
(320,12,7,'Place garlic bulb in cocotte and cover.'),
(321,12,8,'Put butternut squash and garlic in the oven for about 40 minutes or until soft and golden.'),
(322,12,9,'Take out from the oven and transfer squash (whithout peel if you didn\'t peel) and peeled garlic into a pot, add broth, 1 teaspoon very finely chopped fresh Thyme and bring to the boil.'),
(323,12,10,'Once hot, remove from heat and blend with an immersion blender until smooth. Add more broth or water if needed to reach desired consistency.'),
(324,12,11,'Salt and pepper to taste.'),
(325,12,12,'Top with a little pepper and a string of thyme.'),
(326,13,1,'Put the oil, spring/purple onion, cashews and ginger in a pan on medium heat, bring to simmer and cook for 2 minutes'),
(327,13,2,'Add the seame seeds, cook for another 2 minutes, then take off the heat and carefully stir in the soy sauce, vinergar, honey, shichimi togarashi and paprika'),
(328,13,3,'Return the pan to the heat, simmer for 2 minutes more, until slightly reduced, then pour into a bowl and leave to cool to room temperature'),
(329,13,4,'Cut the aubergine in half widthways, then cut each hald into 7cm x 2cm batons. Put these in a bowl with the salt, then transfer to a steaming basket and set aside'),
(330,13,5,'Steam the aubergine for 20 minutes, until soft, then drain and let it cool for a bit'),
(331,13,6,'Transfer the aubergine to a plate, drizzle over the rayou, top with the sprint/purple onion and server at room temperature'),
(332,14,1,'**Preheat the grill** to medium.      Put the cauliflower florets and red onion slices into a roasting tin.      Season, then rub 1 tbsp of the oil into the vegetables. Spread out in a single layer and grill for 10 minutes, turning halfway, or until charred.'),
(333,14,2,'**Meanwhile**, in a bowl, use a fork to whisk together the cornflour, vinegar, Shaoxing rice wine, both soy sauces, and 75ml water until smooth. Set aside.'),
(334,14,3,'**Cook the noodles:**      Bring a pan of salted water to the boil and cook the noodles according to the packet instructions. Drain, rinse under cold water, then divide between 4 bowls.'),
(335,14,4,'**Prepare the sauce:**      Heat 1 tbsp oil in a large frying pan over high heat. Add the garlic and fry for 1 minute, then add the chilli flakes and cashews. Fry for another minute.'),
(336,14,5,'**Combine:**      Reduce the heat to medium, then pour over the sauce. Simmer for 2–3 minutes until thick enough to coat the back of a spoon.'),
(337,14,6,'**Finish:**      When the cauliflower and onion are cooked, spoon straight into the sauce and toss everything together. Serve over the noodles.'),
(338,15,1,'Heat the oil in a casserole, add garlic, bay leaves, coriander and chilli, saute for 1 minute'),
(339,15,2,'Add the leek and salt, cook for 2 minutes, move to the sides of the pan'),
(340,15,3,'Add the chorizo and cook for 4 minutes'),
(341,15,4,'Add the tomatoes and cook for 5 minutes'),
(342,15,5,'Boil the kettle. Add the tomato puree, paprika and rice and mix well'),
(343,15,6,'Pour over 500 ml of water, reduce the heat to low, cover and simmer for 16 minutes'),
(344,15,7,'Turn off the heat and keep covered for another 15 minutes'),
(345,15,8,'Serve with the chopped parsley'),
(346,16,1,'Arrange the oven shelves so that one is in the middle for the cake, and another just below it. Slide a baking sheet onto the lower rack to catch any drips as the cake bakes. Heat the oven to 180°C/160°C Fan/350°F.'),
(347,16,2,'Butter a 22–23cm / 9-inch springform cake tin and line the base with baking parchment. Mix the flour and cocoa powder together in a bowl, and set aside.'),
(348,16,3,'Put the butter, liqueur, sugars, chocolate, coffee and water in a thick-bottomed saucepan and stir over low heat until everything melts and is thickly, glossily smooth. Remove the pan from the heat, and let stand for a couple of minutes.'),
(349,16,4,'Stir the flour and cocoa mixture into the pan, and beat well — just with a spatula or wooden spoon — until all is smooth and glossy again, then gradually beat in the eggs. The mixture will be runny: don’t panic, and don’t add more flour; the chocolate itself sets as it cooks and then cools.'),
(350,16,5,'Pour into the prepared tin until you have covered the base with about 2cm of the mixture (which will be about half of it) and then cover with the raspberries and pour the rest of the mixture on top. You may have to push some of the raspberries back under the cake batter by hand.'),
(351,16,6,'Put into the preheated oven and bake for 40–45 minutes. Don’t try and test by poking in a skewer as you don’t want it to come out clean: the gunge is what the cake is about. But when it’s cooked, the top will be firm, and slightly cracked. Don’t worry about that: a little icing sugar will deflect attention. When it’s ready, take the cake out of the oven and put on a rack. Leave in the tin for 15 minutes before removing the sides of the tin; the cake must stay on its base.'),
(352,16,7,'When you’re just about to eat — and this should be around an hour after the cake’s come out of the oven — dust with a little icing sugar pushed through a tea strainer. Serve with lots more fresh raspberries, and Greek yoghurt, whipped double cream or crème fraîche as wished.   # Additional Information  If you\'re using plain flour rather than self-raising flour, then simply add 2 teaspoons of baking powder to your flour.'),
(353,17,1,'Preheat the oven to 170C. Put two-thirds of the peeled banana chunks into a bowl and mash until smooth. Roughly mash the remainder and stir in gently.'),
(354,17,2,'Sift the flour, baking powder and salt into a bowl, and grease and lightly flour a baking tin about 21x9x7cm.'),
(355,17,3,'Put the sugar, eggs and melted butter in a large bowl and use an electric mixer to whisk them until pale and slightly increased in volume. Fold in the bananas and the dry ingredients until you can see no more flour, then fold in the walnuts.'),
(356,17,4,'Spoon into the tin and bake for about an hour until a skewer inserted into the middle comes out clean. Cool in the tin for 10 minutes before turning out on to a rack to cool completely.'),
(357,18,1,'Pre-heat the oven at 175 degrees'),
(358,18,2,'In a bowl, mix the flour (sifted), baking powder and soda, and salt'),
(359,18,3,'In a different bowl, mix the crushed banana, sugar, stir it, add the peanut butter, stir it, add the oil, milk, egg, vanilla, choco chips and whisk it all'),
(360,18,4,'Add the dry ingredients to the wet ones and combine'),
(361,18,5,'Bake for about 13 minutes, use a stick to test when it\'s done  # Notes  It wasn\'t very tasty, add more banana and peanut butter, maybe skip the cinnamon, more sugar'),
(362,19,1,'Preheat the oven to 200C/180C Fan. Get out a 20cm/8in springform tin and a roll of baking paper. Unfurl a long piece from the roll, and when it looks like you’ve got enough to line the tin with an overhang of 5–7cm/2–2¾in, tear it off and press into the tin and down into the edges at the bottom. Now do the same again with a second piece, placing it perpendicular to the first so that the tin is entirely lined. Push this piece down too and don’t worry about any pleats, creases and wrinkles; this is The Look. Sit something heavy in the tin to keep the paper in place while you get on with the cheesecake mixture.'),
(363,19,2,'I use a mixer fitted with the flat paddle for this. First beat the cream cheese with the sugar until light and smooth; I beat for quite a long time, certainly not under 2 minutes. It is absolutely essential that the cream cheese is at room temperature before you start.'),
(364,19,3,'Beat in the eggs, one at a time, waiting for each one to be incorporated before adding the next. When they’re all mixed in, pour in the soured cream, beating all the while. Once that is also incorporated, you can slow down the mixer a little (or risk getting cornflour all over yourself) and then beat in the salt, followed by the cornflour, a teaspoon at a time. Remove the bowl from the mixer, scrape down the sides with a silicon spatula and give everything a good stir.'),
(365,19,4,'Pour into the lined tin, making sure no cheesecake mixture is left in the bowl. Rap the filled tin on the work surface about five times to get rid of any air bubbles.'),
(366,19,5,'Place in the oven and bake for 50 minutes, until the cheesecake is burnished bronze on top, even chestnut brown in places, and risen, like a dense soufflé. It will, however, still be very jiggly. It’s meant to be. You’ll think it’s undercooked, but it will carry on cooking as it cools, and it should have a soft set anyway.'),
(367,19,6,'Transfer the tin to a wire rack and leave to cool. It will sink in the middle a little, but that too is part of its traditional appearance. I reckon it’s cool enough to eat after 3 hours, although you may need to leave it for a little longer. If you want to chill it in the fridge, do, but not for more than 30 minutes.'),
(368,19,7,'Before serving, unclip and lift the sides of the tin up and away, and then lift the cheesecake up with the edges of the paper. Place this on a board and peel the paper back.'),
(369,20,1,'Heat the oven at 180 celcius'),
(370,20,2,'In a large bowl, mix the eggs and sugar with an electric mixer'),
(371,20,3,'Melt the butter'),
(372,20,4,'Add the butter to the bowl, add the almond flour and cocoa, mix'),
(373,20,5,'Sift the flour, baking powder and yeast to the bowl and mix'),
(374,20,6,'Add the cardamom and mix'),
(375,20,7,'Pour into the mould and cook for about 20 minutes or ready'),
(376,20,8,'Put chocolate whipped cream on top'),
(377,21,1,'Preheat oven to 190°C.'),
(378,21,2,'Mix graham cracker crumbs, sugar, and melted butter.'),
(379,21,3,'Press into a pie pan and bake for 10 minutes.  ### For the Filling'),
(380,21,4,'Lower oven to 175°C.'),
(381,21,5,'Mix condensed milk, yogurt, lime zest, and juice.'),
(382,21,6,'Pour into the crust and bake for 15 minutes.  ### For the Topping'),
(383,21,7,'Whip heavy cream with sugar until peaks form.'),
(384,21,8,'Decorate with whipped cream, lime zest, and slices.'),
(385,22,1,'Preheat oven to 200°C. Line a muffin tin.'),
(386,22,2,'Whisk egg and sugar, add yogurt, oil, cardamom, and rose water. Mix.'),
(387,22,3,'Gradually add dry ingredients.'),
(388,22,4,'Fill liners, top with sesame seeds.'),
(389,22,5,'Bake 8 mins at 200°C, reduce to 175°C, bake 10-12 mins.'),
(390,23,1,'Disuelve la levadura en la leche templada.'),
(391,23,2,'Prepara la masa. Vuelca toda la harina en un bol y añade una pizca de sal. Haz un hueco en el centro y añade la leche con la levadura. Incorpora el huevo, el azúcar, el agua de azahar, la ralladura de una naranja, la ralladura de medio limón y la mantequilla a temperatura ambiente.'),
(392,23,3,'Mezcla todos los ingredientes dentro del bol y pásalo a la maquina cuando ya no puedas trabajar la masa en el bol. Amasa 5-10 minutos (speed 2) hasta que la textura de la masa sea lisa.'),
(393,23,4,'Pon la masa dentro de un recipiente untado con un poco de aceite. Tapa con film de cocina y deja reposar 2 o 3 horas hasta que la masa doble su volumen.'),
(394,23,5,'Quita el aire a la masa. Vuelca la masa sobre el mármol y amasa hasta quitarle el aire. Vuelve a formar una bola y déjala reposar 10 minutos para que la masa se relaje y sea más fácil trabajarla. Forma el roscón. Marca con las manos el agujero en el centro y ve estirando la masa para dar la forma de rosca.'),
(395,23,6,'Pon el roscón sobre una bandeja de horno con papel de horno. Tápalo con film hasta que crezca de nuevo durante una hora y media.'),
(396,23,7,'Píntalo con huevo batido para conseguir un acabado brillante y añade los frutos secos, las frutas escarchadas y el glaseado (Mezcla dos cucharadas de azúcar con una de agua).'),
(397,23,8,'Precalienta el horno a 180 grados con calor arriba y abajo y sin ventilador y hornea durante 20 minutos.'),
(398,23,9,'Abre el roscón por la mitad con un cuchillo de sierra y mucho cuidado.'),
(399,23,10,'Monta la nata con las varillas hasta que espese. Coloca la nata dentro de una manga pastelera. Rellena el roscón y tápalo con cuidado.'),
(400,24,1,'Combine ricotta, milk, egg yolks, and vanilla in a large bowl and whisk until homogenous. Whisk together flour, baking powder, salt, sugar, and lemon zest in a separate bowl. Add the ricotta mixture to the dry ingredients and stir with a wooden spoon until just combined. Some lumps are ok.'),
(401,24,2,'In a separate clean bowl, whisk egg whites until stiff peaks form. Gently fold into batter.'),
(402,24,3,'Heat 1 teaspoon butter in a large non-stick skillet or griddle over medium-low heat until melted. Wipe out with a paper towel. Add four circles of pancake batter using a quarter cup measure. Cook until top side begins to show bubbles, about 2 minutes. Carefully flip and cook until second side is golden brown, about 2 minutes longer. Transfer to a large plate and keep warm in a low oven. Repeat with remaining butter and batter.'),
(403,24,4,'Serve hot with butter, fruit, and syrup.'),
(404,25,1,'Heat the skillet and cook the peppers'),
(405,25,2,'Add the onion'),
(406,25,3,'Add the garlic'),
(407,25,4,'Add the spices'),
(408,25,5,'Add the tomatoes and tomato paste'),
(409,25,6,'Add water if needed, simmer until chick'),
(410,25,7,'Crack the eggs and cook them'),
(411,25,8,'Add the herbs on top'),
(412,26,1,'Combine the yeast and water in the bowl of a stand mixer and stir with a fork until completely dissolved. Add the flour, sugar, eggs and olive oil. With the dough hook, mix on a low speed for 5 minutes to combine. Add the salt and increase the speed to medium for a further 8 minutes (add the raisins 1 minute before finishing). Remove the bowl from the mixer and cover it with a clean, damp tea towel. Leave the dough to rise, well away from any draughts, until it has doubled in size – about 11⁄2–2 hours. Turn the dough out onto a lightly floured surface. Use your hands to punch the air out of it and divide it into thirds. Take each piece in turn, and roll it back and forth to stretch it into a long thin roll about 50cm long.'),
(413,26,2,'Now you’re ready to braid. Take your three logs and press them together at the end furthest away from you, with the central strand pointing directly towards you and the other two roughly at 90° from each other. Cross the right strand over the central one, laying it gently in the space between the central log and the left strand. What was on the right is now in the centre. Lift the left strand over the central log, placing it in the space between the central and right logs. Repeat until the braid is complete.'),
(414,26,3,'Line a baking sheet with baking paper and carefully transfer the cholla onto it. Slip the whole thing into a large plastic bag. Inflate the bag so that the dough doesn’t come into contact with the plastic. Leave to prove again for 11⁄2–2 hours, depending on the temperature of your kitchen. The loaf should be visibly larger, though not doubled in size.'),
(415,26,4,'Meanwhile, preheat the oven to 200°C/gas mark'),
(416,26,5,'Lightly brush the top of the loaf with egg wash, making sure it goes into every fold and crevice. Sprinkle the seeds on top and place in the centre of the oven. Immediately reduce the heat to 180°C/gas mark 4 and bake for 40–45 minutes. Halfway through baking, rotate the baking sheet from front to back to ensure an even bake. The finished cholla should be a glossy, chestnut brown. Cool on the tray for 10–15 minutes before transferring to a wire rack to cool completely.'),
(417,27,1,'Preheat oven 220C with pan inside (I used a cast-iron skillet).'),
(418,27,2,'Mix dry ingredients (flour, sugar, salt, baking powder).'),
(419,27,3,'Mix wet ingredients (egg, oil, milk).'),
(420,27,4,'Combine wet and dry, don\'t overmix, lumpy okay.'),
(421,27,5,'Let batter rest for 20-25 min.'),
(422,27,6,'Butter pan, pour in batter.'),
(423,27,7,'Bake for 20-25 minutes.'),
(424,28,1,'Sift the flour into the bowl of a stand mixer and add all the remaining dough ingredients. Knead with the dough hook on a slow speed for 8–10 minutes until smooth, soft, and elastic.'),
(425,28,2,'Place the dough in an oiled bowl, swiveling it inside the bowl until it is coated with oil on all sides. Cover with a shower cap and leave to rise at room temperature.      - After 45 minutes, punch the risen dough back with your fist, re-cover and leave for another 45 minutes.      - Punch down again and repeat a third time.'),
(426,28,3,'Let the dough rise one last time. Cover a deep baking tray or roasting tin with measuring partchment paper.      - With your fingers, gently coax the dough into a flat shape to cover the tray.      - If the dough resists and springs back, let it relax for another 10 minutes and try again.      - The surface should be nicely cratered with your finger marks – this is what gives focaccia its characteristic dimpled surface.'),
(427,28,4,'Give the dough another 20 minutes to rise a final time while you preheat the oven to **200°C / gas mark 6**.      - Drizzle olive oil generously over the focaccia.      - Sprinkle on the rosemary and sea salt to taste.'),
(428,28,5,'Bake in the oven for 10 minutes, use the bottom rack, then reduce the heat to **180°C / gas mark 4** and continue to bake for a further 15 minutes in the middle rack.      - Check that the base is golden brown and fully baked, even in the center.'),
(429,28,6,'As soon as you take the focaccia out of the oven, drizzle over more olive oil and serve immediately.'),
(430,29,1,'1 In a bowl, mix the flour, salt, sugar, aniseed, sesame, raisins, oil and walnuts'),
(431,29,2,'2 Heat the water, mix the yeast'),
(432,29,3,'3 Add the water/yeast mix to the rest of the ingredients and mix with your hands'),
(433,29,4,'4 Knead for 5 minutes, put the dough in the bowl, cover and wait for at least 2 hours'),
(434,29,5,'5 Degas the dough, split in 6 parts (approx 170gr each) and make 6 balls. Put them in a tray with oven paper and wait 10 minutes'),
(435,29,6,'6 Make discs out of the balls, about 5-7mm thin, then roll them to make the rolls'),
(436,29,7,'7 Put the rolls on the tray, cover with plastic and wait 1 hour'),
(437,29,8,'8 Preheat the oven at 200 degrees, make cuts to the rolls and decorate them with the beaten egg, sesame and sugar'),
(438,29,9,'9 Bake for 25-30 minutes'),
(439,29,10,'Notes: if you want to put the rolls on the fridge overnight, take them out to bring them to room temperature to allow them to grow  Don\'t bake from cold'),
(440,30,1,'Mix the warm water with the honey and yeast, wait until is active.'),
(441,30,2,'Combine the flour, yeast, honey or sugar and the water into the bowl of a stand mixer, and knead with the dough hook for 7 minutes at low speed.'),
(442,30,3,'Add the salt and knead for 3 minutes. Remove the bowl, cover with a clean, damp tea towel, and allow the dough to rise for 60-90 minutes at room temperature until almost doubled in size.'),
(443,30,4,'Turn the dough out onto a lightly floured surface and knead it into a log shape. Using a sharp knife or a dough scraper, divide the log into 16 rolls, each weighing around 40–45g. Shape them into little balls.'),
(444,30,5,'Line a baking sheet with baking paper and dust with flour, then place the rolls on it and place the whole thing inside a large plastic bag (or plastic film, put some flour on top of the rolls to avoid sticking), inflated so that it won’t come into contact with the dough. Allow to rise once more at room temperature, for 60-90 minutes, until doubled in size (note: check after 60 minutes).'),
(445,30,6,'When they are nearly ready, place a baking stone or another baking sheet in the oven and heat the oven to 200°C (no fan). Place a smaller baking tin on the oven floor to act as a water vessel.'),
(446,30,7,'Dust the rolls with a little more flour and make a snip halfway through the middle of each one with a sharp pair of scissors. Before putting the rolls in the oven, tip the ice cubes into the pan on the bottom. (This will help to form a better crust.)'),
(447,30,8,'Quickly take the baking stone out of the oven and in one swift motion, slide the baking paper with the rolls on it onto the hot stone. Place the rolls in the centre of the oven and bake for 13–15 minutes until the bottom of the rolls are golden brown. They should open up like little tulips as they bake.'),
(448,30,9,'Transfer to a wire rack to cool for 10–15 minutes.'),
(449,31,1,'Mix everything in a pot, cook at medium heat until it\'s boiling'),
(450,31,2,'Reduce the heat to low and cook for about 10 minutes'),
(451,31,3,'Use a colander to strain it'),
(452,31,4,'Now you can put it in the fridge to drink it later or in the freezer for 3 hours'),
(453,31,5,'If you put it in the freezer, blend it and you have ice cream'),
(454,32,1,'Mix the flour and water.'),
(455,32,2,'Remove foam, cover with cling film and wait for 4 hours.'),
(456,32,3,'Add oil, salt and rosemary.'),
(457,32,4,'Pour into a dish, bake for 210 (no fan) for 30 minutes..'),
(458,33,1,'Trocea todo, bate el tomate y pon el pan en remojo, añade el ajo y la sal, bate todo, añade el aceite y bate más.'),
(459,34,1,'Mix  the yogurt, egg and oil in a bowl'),
(460,34,2,'In a separate bowl, mix the rest of the ingredients'),
(461,34,3,'Mix both, don\'t overmix'),
(462,34,4,'Cook at medium heat for 2-3 minutes each side'),
(463,35,1,'Dice the onion and mince the garlic. Place both in a slow cooker.'),
(464,35,2,'Add the crushed tomatoes, tomato paste, basil, oregano, brown sugar, balsamic vinegar, and butter to the slow cooker. Stir everything together well.'),
(465,35,3,'Place the lid on the slow cooker and cook on high for four hours or low for eight hours.'),
(466,35,4,'After cooking, give it a good stir, then add salt to taste.'),
(467,36,1,'Add both flours, the sugar, baking powder and salt to the bowl of a food processor and stir with a spoon until fully combined. Add the butter and blitz until the mixture resembles sand. Add the egg and blitz again until the mixture resembles soft flakes. Transfer it to a clean and dry worktop and crush it with your hands to bind the flakes together, then pat it down with the palm of your hand. Using a straight-edge scraper, lift one side and fold it over. Repeat the patting and folding a few times until the dough feels smooth and pliable. Flatten to about 2cm thickness, wrap in clingfilm and chill in the fridge for at least 30 minutes.'),
(468,36,2,'When ready to bake, place the shelf in the middle of the oven and preheat it to 160C fan/gas mark'),
(469,36,3,'Line 2 baking trays with baking paper or silicone mats. Take the dough out of the fridge and roll it out to 8mm thickness on a lightly floured worktop. Cut circles in the dough with a 4cm pastry cutter, then arrange them on the lined baking sheets, spacing them 2-3cm apart. Offcuts can be reworked and re-rolled to make more cookies. Pinch the top of each biscuit to shape them as chestnuts, then bake one tray at a time for about 10 minutes. Allow the cookies to cool on the tray for a couple of minutes before transferring them to a wire rack to cool completely. Keep the baking paper for the next step.'),
(470,36,4,'Put the chocolate in a small bowl and microwave it for 1 minute, then stir well and keep microwaving it in 10-second bursts, stirring it well between subsequent bursts until completely melted. Set aside to cool for a few minutes. Holding one cookie by the bottom of the chestnut shape, dip it pointed-end first into the chocolate to coat about three-quarters of the cookie. Tilt it from side to side to give the coating a curved edge, then place it on the baking paper to set. Repeat with the rest. Castagnotti keep for up to a week in a biscuit tin.'),
(471,37,1,'in a pan, mix the flour and water, cook for a few minutes at low temp until rubbery'),
(472,37,2,'spread on a sheet, using parchment paper'),
(473,37,3,'cut it into fries and fry \'em'),
(474,38,1,'Soak the pulses in cold water overnight'),
(475,38,2,'Pulse the beans first, medium coarse and set aside'),
(476,38,3,'Pulse the onions, garlic, herbs, fine minced'),
(477,38,4,'Add the beans and spices back and pulse again'),
(478,38,5,'Transfer it all to a bowl and add the baking powder'),
(479,38,6,'Make the balls/discs, add sesame seeds  and fry at 175 celcius'),
(480,39,1,'Preheat oven at 200, grease muffin tin'),
(481,39,2,'Mix the oil, parmesan, tomato puree, oregano eggs, salt, yogurt, crumbled feta, quartered cherry tomatoes and black pepper'),
(482,39,3,'Add the flour, baking powder, bicarbonate of soda, stir enough to combine'),
(483,39,4,'Add the mixture to the tin, top each with 2 tomato halves, feta and oregano'),
(484,39,5,'Bake for 15 minutes'),
(485,39,6,'Cool for 10-15 minutes before easing from the tin');
/*!40000 ALTER TABLE `instructions` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `meal_plans`
--

DROP TABLE IF EXISTS `meal_plans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `meal_plans` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plan_date` datetime NOT NULL,
  `recipe_id` int DEFAULT NULL,
  `custom_meal_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `recipe_id` (`recipe_id`),
  KEY `ix_meal_plans_id` (`id`),
  CONSTRAINT `meal_plans_ibfk_1` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meal_plans`
--

LOCK TABLES `meal_plans` WRITE;
/*!40000 ALTER TABLE `meal_plans` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `meal_plans` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `notes`
--

DROP TABLE IF EXISTS `notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `notes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `recipe_id` int DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `text` text NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `recipe_id` (`recipe_id`),
  KEY `ix_notes_id` (`id`),
  CONSTRAINT `notes_ibfk_1` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notes`
--

LOCK TABLES `notes` WRITE;
/*!40000 ALTER TABLE `notes` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `notes` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `recipe_tags`
--

DROP TABLE IF EXISTS `recipe_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `recipe_tags` (
  `recipe_id` int NOT NULL,
  `tag_id` int NOT NULL,
  PRIMARY KEY (`recipe_id`,`tag_id`),
  KEY `tag_id` (`tag_id`),
  CONSTRAINT `recipe_tags_ibfk_1` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recipe_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipe_tags`
--

LOCK TABLES `recipe_tags` WRITE;
/*!40000 ALTER TABLE `recipe_tags` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `recipe_tags` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `recipes`
--

DROP TABLE IF EXISTS `recipes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `recipes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `photo_path` varchar(500) DEFAULT NULL,
  `servings` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_recipes_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes`
--

LOCK TABLES `recipes` WRITE;
/*!40000 ALTER TABLE `recipes` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `recipes` VALUES
(1,'Basmati rice with chickpeas, currants & herbs','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(2,'Upside-down apricot, pistachio & olive oil cake','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(3,'Cauliflower potato curry','uploads/chef-hat.jpg','None','2025-10-20 11:28:17','2025-10-20 11:28:17'),
(4,'Chicken rice','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(5,'Chinese stuffed pancake','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(6,'Czech soup','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(7,'Date chickpea curry','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(8,'Katsu curry','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(9,'Korean garlic tofu','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(10,'Pappardelle with nduja','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(11,'Potato omelette','13b29fb0-e655-4cf0-81aa-93f00c4c21c9.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(12,'Pumpkin soup','placeholder.jpg','None','2025-10-20 11:26:50','2025-10-20 11:26:50'),
(13,'Steamed aubergines with cashew','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(14,'Sticky cauliflower noodles','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(15,'Tomato rice with chorizo','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(16,'Chocolate raspberry cake','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(17,'Banana bread','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(18,'Banana peanut muffins','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(19,'Basque cheesecake','6b6c7f9b-4e1e-4efc-8d63-a2c887dd8767_updated_40679794-2959-4074-9007-4e59dcbbc0ce.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(20,'Chocolate coca','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(21,'Key lime pie','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(22,'Persian Cardamom Muffins','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(23,'Roscon de reyes','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(24,'Ricotta pancakes','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(25,'Shakshuka','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(26,'Challah','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(27,'Cornbread','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(28,'Focaccia','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(29,'Oil bread rolls','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(30,'Spelt rolls','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(31,'Leche rizada','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(32,'Farinata','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(33,'Salmorejo','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(34,'Savory pancakes','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(35,'Marinara','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(36,'Chestnut cookies','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(37,'Chickpea fries','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(38,'Falafel','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50'),
(39,'Tomato feta muffins','placeholder.jpg',NULL,'2025-10-20 11:26:50','2025-10-20 11:26:50');
/*!40000 ALTER TABLE `recipes` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_tags_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;
commit;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-10-20 12:08:54
