#!/usr/bin/env python3
"""Phase 0/1 transport topology tests; source disconnections are EXPECTED.

This baseline test does not waive road-connectivity acceptance: --check will
remain red until the later authored connectors pass a separate release gate.
"""
import math
import os
import sys
import unittest

sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from frontier_routes import (Route,RouteGraph,ROUTE_GRAPH,ROUTE_SOURCES,
                             segment_intersection,nearest_route_anchor,route_path)
from new_austellia import ROADS,RAILS,TOWNS,MAJOR_TOWNS
from frontier_world import WAYSTATIONS,START_SPUR
from tools.audit_routes import audit

class RouteGeometryTest(unittest.TestCase):
 def test_baseline_inventory(self):
  self.assertEqual(len(ROADS),13)
  self.assertEqual(len(RAILS),4)
  self.assertEqual(len(TOWNS),35)
  self.assertEqual(len(MAJOR_TOWNS),12)
  self.assertEqual(len(WAYSTATIONS),13)
  self.assertEqual(len(ROUTE_SOURCES),18)
  self.assertEqual(ROUTE_SOURCES[-1].vertices,START_SPUR)

 def test_segment_crossing_and_non_crossing(self):
  hit=segment_intersection((0,0),(10,10),(0,10),(10,0))
  self.assertIsNotNone(hit)
  self.assertAlmostEqual(hit[0],.5)
  self.assertEqual(segment_intersection((0,0),(10,0),(0,2),(10,2)),None)
  self.assertEqual(segment_intersection((0,0),(10,0),(11,-2),(11,2)),None)
  self.assertIsNotNone(segment_intersection((0,0),(10,0),(5,-2),(5,0)))

 def test_exact_midsegment_intersection_builds_junction(self):
  roads=(Route("a","wagon",((0,0),(10,0))),
         Route("b","wagon",((5,-5),(5,5))))
  graph=RouteGraph(roads)
  self.assertEqual(len(graph.components("wagon")),1)
  self.assertIsNotNone(graph.path((0,0),(5,5)))
  self.assertEqual(len(graph.edges),4)

 def test_train_tracks_never_join_wagon(self):
  roads=(Route("a","wagon",((0,0),(10,0))),
         Route("b","rail",((5,-5),(5,5))))
  graph=RouteGraph(roads)
  self.assertEqual(len(graph.components("wagon")),1)
  self.assertEqual(len(graph.components("rail")),1)
  rail_tip=next(n for n,p in graph.nodes.items() if p==(5,5))
  self.assertIsNone(graph.path((0,0),rail_tip,mode="wagon"))

 def test_unconnected_parallel_routes_not_snapped(self):
  roads=(Route("a","wagon",((0,0),(10,0))),
         Route("b","wagon",((0,3),(10,3))))
  graph=RouteGraph(roads)
  self.assertEqual(len(graph.components("wagon")),2)

 def test_baseline_reports_existing_gaps(self):
  report=audit()
  self.assertEqual(report["source"]["wagon_polylines"],13)
  self.assertEqual(report["source"]["waystations"],13)
  self.assertGreater(len(report["graph"]["disconnected_or_missing_road_core_ids"]),0)
  self.assertGreater(len(report["graph"]["wagon_routes"]),1)
  self.assertIn("brimstone",set(x["id"] for x in report["sites"]))
  self.assertIn("calhoun_island",report["known_exemptions"])
  self.assertTrue(any(s["id"]=="brimstone" and s["distance_to_wagon"]>400
                      for s in report["sites"]))
  self.assertEqual(len(report["crossings"]),len(__import__('new_austellia').BRIDGES))

 def test_deterministic_topology_and_anchor(self):
  again=RouteGraph()
  self.assertEqual(len(ROUTE_GRAPH.nodes),len(again.nodes))
  self.assertEqual(len(ROUTE_GRAPH.edges),len(again.edges))
  self.assertEqual(ROUTE_GRAPH.route_component_ids(),again.route_component_ids())
  a=nearest_route_anchor(*ROADS[0][0],max_distance=100)
  self.assertIsNotNone(a)
  self.assertLess(a["distance"],1)
  self.assertIsNotNone(route_path(ROADS[0][0],ROADS[0][-1]))

if __name__=="__main__":unittest.main()
