from app.usage_metering import *

def test_meter_totals_are_customer_scoped():
    meter=UsageMeter()
    meter.record(UsageEvent("1","cust-a","v1",UsageEventType.COMPLETED,100,2.5,1))
    meter.record(UsageEvent("2","cust-a","v2",UsageEventType.UNCERTAIN,50,1.5,2))
    meter.record(UsageEvent("3","cust-b","v3",UsageEventType.COMPLETED,999,9,9))
    assert meter.totals("cust-a")=={"verification_events":2,"processing_time_ms":150,"compute_units":4,"external_api_calls":3}

def test_negative_usage_is_rejected():
    meter=UsageMeter()
    try: meter.record(UsageEvent("1","c","v",UsageEventType.FAILED,-1))
    except ValueError: pass
    else: raise AssertionError("negative usage accepted")

def test_usage_digest_is_deterministic():
    e=UsageEvent("1","c","v",UsageEventType.COMPLETED,100,2,1)
    assert usage_digest(e)==usage_digest(e)
