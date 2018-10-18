"""
Compute the p-value for a graph

"""

import os
import sys
import optparse
import functools
import operator
import logging
from fixrgraph.stat_sig.feat import (FeatExtractor, Feat)
from fixrgraph.stat_sig.db import FeatDb

def compute_p_value(graph_path,
                    featDb):
    featExtractor = FeatExtractor(graph_path)

    methodCalls = set()
    methodEdges = set()

    # Extract the features
    for feat in featExtractor.features:
        if feat.kind == Feat.METHOD_CALL:
            methodCalls.add(feat)
        elif feat.kind == Feat.METHOD_EDGE:
            methodEdges.add(feat)
        else:
            raise Exception("Unknown feature kind " + feat.kind)

    # Compute the probability of the null model
    #
    # methodCalls = {m1, ..., mk}
    # methodEdges = {e1, ..., el}
    #
    # We compute P(e1 = 1, ..., el = 1 | m1, ..., mk) for the null model.
    #
    # We assume e1, ..., el to be independent. Then:
    # P(e1 = 1, ..., el = 1) = P(e1 = 1 | m1, ..., mk) ... P(el = 1 | m1, ..., mk)
    #
    # We compute each P(ei = 1 | m1, ..., mk) as:
    # P(ei = 1 | m1, ..., mk ) = P(ei=1, m1 = 1, ..., mk =1) / P(ei = 1)
    #
    methodEdgesProb = []
    for e in methodEdges:
        # P(ei=1, m1 = 1, ..., mk =1)
        prob_all = featDb.count_features([e] + list(methodCalls))
        # P(ei = 1)
        prob_e = featDb.count_features([e])
        # P(ei = 1 | m1, ..., mk )
        cond_prob = float(prob_all) / float(prob_e)
        methodEdgesProb.append(cond_prob)

        logging.info("Computing %d/%d = %f" % (prob_all, prob_e, cond_prob) )


    p_value = functools.reduce(operator.mul, methodEdgesProb, 1.0)
    logging.debug("Computed pvalue %f" % p_value)

    
    

    featDb.insert_pval(featExtractor.graph_sig, p_value)

    return p_value

def compute_p_values(graph_path,
                     host,
                     user,
                     password,
                     db_name = "groum_features"):
    featDb = FeatDb(host, user, password, db_name)
    featDb.open()

    acdfgs = []
    for root, dirs, files in os.walk(graph_path, topdown=False):
        for name in files:
            if name.endswith("acdfg.bin"):
                filename = os.path.join(root, name)
                acdfgs.append(filename)

    i = 0
    for filename in acdfgs:
        i = i + 1

        perc = float(i) / float(len(acdfgs))
        perc = perc * 100

        print "Extracting %d/%d (%f)..." % (i, len(acdfgs), perc)
        compute_p_value(filename, featDb)

    featDb.close()


def main():
    p = optparse.OptionParser()
    p.add_option('-g', '--graphs', help="Path to the groum files")

    p.add_option('-a', '--host', help="Address to the db server")
    p.add_option('-u', '--user', help="User to access the db")
    p.add_option('-p', '--password', help="Password to the db")

    def usage(msg=""):
        if msg:
            print "----%s----\n" % msg
        p.print_help()
        sys.exit(1)

    opts, args = p.parse_args()

    required = [opts.graphs,opts.host,opts.user,opts.password]
    for r in required:
        if (not r):
            usage("Missing required argument!")
    if (not os.path.exists(opts.graphs)): usage("Path %s does not exists!" % opts.graphs)

    compute_p_values(opts.graphs,
                     opts.host,
                     opts.user,
                     opts.password)

    print "Computed p values"


if __name__ == '__main__':
    main()

