'''
Test cases for stix2patterns/validator.py.
'''

import pytest

from stix2patterns.validator import validate

###############################################################################
# EXAMPLES FROM PATTERNING SPEC
###############################################################################

SPEC_CASES = [
    """[file:hashes."SHA-256" = 'aec070645fe53ee3b3763059376134f058cc337247c978add178b6ccdfb0019f']""",
    """[email-message:from_ref.value MATCHES '.+\\@example\\.com$' AND email-message:body_multipart[*].body_raw_ref.name MATCHES '^Final Report.+\\.exe$']""",
    """[file:hashes."SHA-256" = 'aec070645fe53ee3b3763059376134f058cc337247c978add178b6ccdfb0019f' AND file:mime_type = 'application/x-pdf']""",
    ("""[file:hashes."SHA-256" = 'bf07a7fbb825fc0aae7bf4a1177b2b31fcf8a3feeaf7092761e18c859ee52a9c' OR """
        """file:hashes.MD5 = 'cead3f77f6cda6ec00f57d76c9a6879f'] AND """
        """[file:hashes."SHA-256" = 'aec070645fe53ee3b3763059376134f058cc337247c978add178b6ccdfb0019f']"""),
    """[file:hashes.MD5 = '79054025255fb1a26e4bc422aef54eb4'] FOLLOWEDBY [win-registry-key:key = 'HKEY_LOCAL_MACHINE\\foo\\bar'] WITHIN 300 SECONDS""",
    ("""[user-account:account_type = 'unix' AND user-account:user_id = '1007' AND user-account:account_login = 'Peter'] AND """
        """[user-account:account_type = 'unix' AND user-account:user_id = '1008' AND user-account:user_id = 'Paul'] AND """
        """[user-account:account_type = 'unix' AND user-account:user_id = '1009' AND user-account:user_id = 'Mary']"""),
    """[artifact:mime_type = 'application/vnd.tcpdump.pcap' AND artifact:payload_bin MATCHES '\\xd4\\xc3\\xb2\\xa1\\x02\\x00\\x04\\x00']""",
    """[file:name = 'foo.dll' AND file:parent_directory_ref.path = 'C:\\Windows\\System32']""",
    """[file:extensions.windows-pebinary-ext.sections[*].entropy > 7.0]""",
    """[file:mime_type = 'image/bmp' AND file:magic_number_hex = h'ffd8']""",
    """[network-traffic:dst_ref.type = 'ipv4-addr' AND network-traffic:dst_ref.value = '203.0.113.33/32']""",
    """[network-traffic:dst_ref.type = 'domain-name' AND network-traffic:dst_ref.value = 'example.com'] REPEATS 5 TIMES WITHIN 1800 SECONDS""",
    """[domain-name:value = 'www.5z8.info' AND domain-name:resolves_to_refs[*].value = '198.51.100.1/32']""",
    """[url:value = 'http://example.com/foo' OR url:value = 'http://example.com/bar']""",
    """[x509-certificate:issuer = 'CN=WEBMAIL' AND x509-certificate:serial_number = '4c:0b:1d:19:74:86:a7:66:b4:1a:bf:40:27:21:76:28']""",
    ("""[windows-registry-key:key = 'HKEY_CURRENT_USER\\Software\\CryptoLocker\\Files' OR """
        """windows-registry-key:key = 'HKEY_CURRENT_USER\\Software\\Microsoft\\CurrentVersion\\Run\\CryptoLocker_0388']"""),
    """[(file:name = 'pdf.exe' OR file:size = '371712') AND file:created = t'2014-01-13T07:03:17Z']""",
    """[email-message:sender_ref.value = 'jdoe@example.com' AND email-message:subject = 'Conference Info']""",
    """[x-usb-device:usbdrive.serial_number = '575833314133343231313937']""",
    ("""[process:arguments = '>-add GlobalSign.cer -c -s -r localMachine Root'] FOLLOWEDBY """
        """[process:arguments = '>-add GlobalSign.cer -c -s -r localMachineTrustedPublisher'] WITHIN 300 SECONDS"""),
    """[network-traffic:dst_ref.value ISSUBSET '2001:0db8:dead:beef:0000:0000:0000:0000/64']""",
    """([file:name = 'foo.dll'] AND [win-registry-key:key = 'HKEY_LOCAL_MACHINE\\foo\\bar']) OR [process:name = 'fooproc' OR process:name = 'procfoo']""",
]


@pytest.mark.parametrize("test_input", SPEC_CASES)
def test_spec_patterns(test_input):
    '''
    Validate patterns from STIX 2.0 Patterning spec.
    '''
    pass_test = validate(test_input, print_errs=True)
    assert pass_test is True


###############################################################################
# TEST CASES EXPECTED TO FAIL
###############################################################################
FAIL_CASES = [
    "file:size = 1280",  # Does not use square brackets
    "[file:hashes.MD5 = cead3f77f6cda6ec00f57d76c9a6879f]"  # No quotes around string
    "[file.size = 1280]",  # Use period instead of colon
    "[file:name MATCHES /.*\\.dll/]",  # Quotes around regular expression
    # TODO: add more failing test cases.
]


@pytest.mark.parametrize("test_input", FAIL_CASES)
def test_fail_patterns(test_input):
    '''
    Validate that patterns fail as expected.
    '''
    pass_test = validate(test_input, print_errs=True)
    assert pass_test is False


###############################################################################
# TEST CASES EXPECTED TO PASS
###############################################################################
PASS_CASES = [
    "[file:size = 1280]",
    "[file:size != 1280]",
    "[file:size < 1024]",
    "[file:size <= 1024]",
    "[file:size > 1024]",
    "[file:size >= 1024]",
    "[file:file_name = 'my_file_name']",
    "[file:extended_properties.ntfs-ext.sid = '234']",
    "[emailaddr:value MATCHES '.+\@ibm\.com$' OR file:name MATCHES '^Final Report.+\.exe$']",
    "[ipv4addr:value ISSUBSET '192.168.0.1/24']",
    "[ipv4addr:value NOT ISSUBSET '192.168.0.1/24']",
    "[user-account:value = 'Peter'] AND [user-account:value != 'Paul'] AND [user-account:value = 'Mary'] WITHIN 5 MINUTES",
    "[file:file_system_properties.file_name LIKE 'name%']",
    "[file:file_name IN ('test.txt', 'test2.exe', 'README')]",
    "[file:size IN (1024, 2048, 4096)]",
    "[network-connection:extended_properties[0].source_payload MATCHES 'dGVzdHRlc3R0ZXN0']",
    "[win-registry-key:key = 'hkey_local_machine\\foo\\bar'] WITHIN 5 MILLISECONDS",
    "[win-registry-key:key = 'hkey_local_machine\\foo\\bar'] WITHIN 5 SECONDS",
    "[win-registry-key:key = 'hkey_local_machine\\foo\\bar'] WITHIN 5 HOURS",
    "[win-registry-key:key = 'hkey_local_machine\\foo\\bar'] WITHIN 5 DAYS",
    "[win-registry-key:key = 'hkey_local_machine\\foo\\bar'] WITHIN 5 MONTHS",
    "[win-registry-key:key = 'hkey_local_machine\\foo\\bar'] WITHIN 5 YEARS"
]


@pytest.mark.parametrize("test_input", PASS_CASES)
def test_pass_patterns(test_input):
    '''
    Validate that patterns pass as expected.
    '''
    pass_test = validate(test_input, print_errs=True)
    assert pass_test is True
