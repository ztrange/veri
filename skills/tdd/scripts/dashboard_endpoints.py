# dashboard_endpoints.py — the server dashboard.sh execs: a delegate to veri/dashboard.py.
# Usage: dashboard_endpoints.py <dashboard.html> <port> <status.sh> <metrics.sh>
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "veri"))

import dashboard

dashboard.status_sh = sys.argv[3]
dashboard.metrics_sh = sys.argv[4]

if __name__ == "__main__":
    sys.exit(dashboard.main(sys.argv[2:3]))
sys.modules[__name__] = dashboard
