import dbus
from subprocess import run
import vobject


def get_modem_path():
    # Connect to the system bus
    bus = dbus.SystemBus()

    # Get the ofono Manager object
    manager = bus.get_object('org.ofono', '/')

    # Get the Manager interface
    manager_iface = dbus.Interface(manager, 'org.ofono.Manager')

    # List modems
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
    # Connect to the system bus
    bus = dbus.SystemBus()

    # Get the VoiceCallManager interface of the modem
    voice_call_manager = bus.get_object('org.ofono', modem_path)
    voice_call_manager_iface = dbus.Interface(voice_call_manager, 'org.ofono.VoiceCallManager')

    # Get active calls
    calls = voice_call_manager_iface.GetCalls()

    # Hang up each active call
    for call in calls:
        state = call[1]['State']

        if state == 'incoming':
            line_identification = call[1]['LineIdentification']
            contacts = read_vcf()
            contact_name = [contact.fn.value for contact in contacts
                            if hasattr(contact, 'tel') and line_identification in contact.tel.value.replace(' ', '')]
            contact_name = contact_name[0]

            call_path = call[0]
            call_iface = dbus.Interface(bus.get_object('org.ofono', call_path), 'org.ofono.VoiceCall')
            notification_output = run(['/usr/bin/notify-send', '-A', 'Aceptar', '-A', 'Ignorar', '-A', 'Colgar', '-t', '15000',
                 f'"Llamada de {contact_name}"'], capture_output=True).stdout
            if b'0' in notification_output:
                call_iface.Answer()
            elif b'2' in notification_output:
                call_iface.Hangup()


def read_vcf():
    with open('contacts.vcf', 'r') as vcf_file:
        contacts_data = vcf_file.read()
    contacts = vobject.readComponents(contacts_data)
    return contacts
