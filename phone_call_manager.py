import dbus
from subprocess import run
import vobject


def get_modem_path():
    bus = dbus.SystemBus()
    manager = bus.get_object('org.ofono', '/')
    manager_iface = dbus.Interface(manager, 'org.ofono.Manager')
    modems = manager_iface.GetModems()

    # Look for the modem with Bluetooth (hfp)
    for modem in modems:
        if 'hfp' in modem[1].get('Type', ''):
            return modem[0]
    return None


def caller(modem_path, phone_number):
    # Connect to the system bus
    bus = dbus.SystemBus()

    # Get the VoiceCallManager interface of the modem
    voice_call_manager = bus.get_object('org.ofono', modem_path)
    voice_call_manager_iface = dbus.Interface(voice_call_manager, 'org.ofono.VoiceCallManager')

    # Dial the phone number
    voice_call_manager_iface.Dial(phone_number, "")


def call_management(modem_path):
    # Get active calls
    call, bus = get_call(modem_path)

    if call is None:
        return

    # Manage active call
    state = call[1]['State']

    if state == 'incoming':
        line_identification = call[1]['LineIdentification']
        contacts = read_vcf()
        contact_name = [contact.fn.value for contact in contacts
                        if hasattr(contact, 'tel') and line_identification in contact.tel.value.replace(' ', '')]
        if len(contact_name) > 0:
            contact_name = contact_name[0]
        else:
            contact_name = line_identification

        call_path = call[0]
        call_iface = dbus.Interface(bus.get_object('org.ofono', call_path), 'org.ofono.VoiceCall')
        notification_output = run(['/usr/bin/notify-send', '-A', 'Aceptar', '-A', 'Colgar', '-t', '15000',
                                   f'"Llamada de {contact_name}"'], capture_output=True).stdout
        if b'0' in notification_output:
            call_iface.Answer()
        elif b'1' in notification_output:
            call_iface.Hangup()


def get_call(modem_path):
    # Connect to the system bus
    bus = dbus.SystemBus()
    # Get the VoiceCallManager interface of the modem
    voice_call_manager = bus.get_object('org.ofono', modem_path)
    voice_call_manager_iface = dbus.Interface(voice_call_manager, 'org.ofono.VoiceCallManager')

    # Get active calls
    calls = voice_call_manager_iface.GetCalls()
    for call in calls:
        return call, bus
    return None, bus


def hang_out_call(modem_path):
    # Get active calls
    try:
        call, bus = get_call(modem_path)
        call_path = call[0]
        call_iface = dbus.Interface(bus.get_object('org.ofono', call_path), 'org.ofono.VoiceCall')
        # Hang Out Call
        call_iface.Hangup()
        return True
    except TypeError:
        return False


# TODO Have to implement full compatibility with PBAP instead of updating contacts manually
def read_vcf():
    with open('contacts.vcf', 'r') as vcf_file:
        contacts_data = vcf_file.read()
    contacts = vobject.readComponents(contacts_data)
    return contacts
