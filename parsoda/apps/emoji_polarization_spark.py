import argparse
from datetime import date

from pyspark import SparkContext, SparkConf

from parsoda import SocialDataApp
from parsoda.function.analysis.gap_bide_analysis import GapBIDE
from parsoda.function.analysis.two_factions_polarization import TwoFactionsPolarization
from parsoda.function.crawling.local_file_crawler import LocalFileCrawler
from parsoda.function.crawling.parsing.flickr_parser import FlickrParser
from parsoda.function.crawling.parsing.twitter_parser import TwitterParser
from parsoda.function.crawling.parsing.vinitaly2019_parser import Vinitaly2019Parser
from parsoda.function.filtering import IsGeotagged, IsInPlace, IsInRoI, HasEmoji
import sys

from parsoda.function.mapping.classify_by_emoji import ClassifyByEmoji
from parsoda.function.reduction.reduce_by_emoji_polarity import ReduceByEmojiPolarity
from parsoda.function.visualization.print_emoji_polarization import PrintEmojiPolarization
from parsoda.model.driver.parsoda_pyspark_driver import ParsodaPySparkDriver
from parsoda.utils.roi import RoI

def parse_command_line():
    parser = argparse.ArgumentParser(description='Emoji Polarization')
    parser.add_argument("--partitions", "-p",
                        type=int,
                        default=-1,
                        help="specifies the number of data partitions.")
    parser.add_argument("--chunk-size", "-c",
                        type=int,
                        default=128,
                        help="specifies the size of data partitions in megabytes.")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_command_line()

    #driver = ParsodaSingleCoreDriver()
    #driver = ParsodaMultiCoreDriver(4)
    driver = ParsodaPySparkDriver(SparkContext(conf=SparkConf()))
    #driver = ParsodaPyCompssDriver()

    app = SocialDataApp("Emoji Polarization", driver, num_partitions=args.partitions, chunk_size=args.chunk_size)

    app.set_crawlers([
        # reads the same dataset more times for reaching a total dimension of data >=10GB
        LocalFileCrawler('/root/tmpfs/TwitterRome2017.json', TwitterParser()) for i in range(3)
        #LocalFileCrawler('/root/tmpfs/TwitterRome2017_6X.json', TwitterParser()),
        
        # LocalFileCrawler('./resources/input/TwitterRome2017_100k.json', TwitterParser()),
        # LocalFileCrawler('./resources/input/flickr100k.json', FlickrParser()),
        # LocalFileCrawler('./resources/input/vinitaly2019.json', Vinitaly2019Parser()),
    ])
    app.set_filters([
        HasEmoji()
    ])
    app.set_mapper(ClassifyByEmoji("./resources/input/emoji.json"))
    app.set_reducer(ReduceByEmojiPolarity())
    app.set_analyzer(TwoFactionsPolarization())
    app.set_visualizer(PrintEmojiPolarization('./resources/output/emoji_polarization.txt'))

    app.execute()
