from pylsl import StreamInfo, StreamOutlet

# Global outlet instance (created once per process)
_outlet = None

def get_trigger_outlet():
    """
    Get or create the trigger outlet
    CRITICAL: All files must use IDENTICAL stream parameters
    """
    global _outlet
    if _outlet is None:
        info = StreamInfo(
            name='Trigger1',
            type='Markers',
            channel_count=1,
            nominal_srate=0,  # Irregular rate for event-based data
            channel_format='string',
            source_id='SCANS'  # MUST be same everywhere!
        )
        _outlet = StreamOutlet(info)
        print("Trigger outlet created")
    return _outlet


def send_trigger(value):
    """
    Send a trigger to the LSL stream
    
    Args:
        value: Trigger value (will be converted to string)
    
    Example:
        send_trigger("stimulus_onset")
        send_trigger(1)
        send_trigger("response_correct")
    """
    outlet = get_trigger_outlet()
    outlet.push_sample([str(value)])


# Test code
if __name__ == "__main__":
    import time
    
    print("Testing trigger sender...\n")
    
    test_triggers = [
        "test_start",
        "stimulus_1",
        "response",
        "feedback",
        "test_end"
    ]
    
    for trigger in test_triggers:
        send_trigger(trigger)
        print(f"✓ Sent: {trigger}")
        time.sleep(0.5)