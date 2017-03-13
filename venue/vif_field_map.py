from typing import Tuple, Dict

VIF_FIELD_MAP = {
    'hdr': {
        1: ('exporting_program', str),
        2: ('export_datetime', str),
        3: ('vif_filename', str),
        4: ('vif_detail', int)},
    'vrq': {
        1: ('site_name', str),
        2: ('packet_id', str),
        3: ('request_code', int),
        4: ('comment', str),
        8: ('auth_info', str),
        9: ('gateway_type', int)},
    'vrp': {
        1: ('site_name', str),
        2: ('packet_id', str),
        3: ('response_code', int),
        4: ('error_number', int),
        5: ('response_text', str)},
    'ins': {
        2: ('name', str),
        3: ('group_name', str),
        4: ('location_code', str),
        5: ('company_code', int),
        6: ('location_number', int),
        7: ('country', str),
        8: ('name_duplicate', str),
        9: ('gl_company_index', int),
        10: ('gl_state_code', str),
        11: ('gl_location_code', str),
        12: ('gl_start_date', str),
        13: ('group_code', str),
        14: ('abn', str),
        15: ('state', str)},
    'dis': {
        2: ('name', str),
        3: ('code', str),
        13: ('abn', str)},
    'rat': {
        1: ('id', int),
        2: ('name', str),
        3: ('code', str),
        4: ('synopsis', str),
        5: ('restricted_rating', bool)},
    'mov': {
        2: ('rating_code', str),
        3: ('name', str),
        4: ('abbreviation', str),
        5: ('movie_code', str),
        6: ('distributor_code', str),
        7: ('length', int),
        8: ('first_date', str),
        9: ('last_date', str),
        10: ('end_no_free_list_date', str),
        11: ('synopsis', str),
        12: ('gateway_code', str),
        13: ('english_title', str),
        14: ('release_date', str),
        15: ('long_name', str),
        16: ('reference_number', int),
        17: ('policy', str),
        18: ('locations', str),
        19: ('talent', str),
        20: ('sound', str),
        21: ('consumer_advice', str),
        22: ('genre', str),
        23: ('sneak_date', str),
        24: ('number_of_prints', int),
        25: ('open_caption', bool),
        26: ('enabled', bool),
        27: ('ho_lock', bool),
        28: ('display_format', int),  # 0=2D, 1=3D, 2=4D
        29: ('print_type', int),  # 0=Film, 1=1.5K digital, 2=2K, 3=4K
        101: ('url', str)},
    'tkt': {
        2: ('name', str),
        3: ('code', str),
        4: ('comment', str),
        5: ('commencement_date', str),
        6: ('expiry_date', str),
        7: ('key_1', int),
        8: ('key_2', int),
        9: ('shift_category_code', str),
        10: ('cashbook_code', str),
        11: ('points', int),
        12: ('seats', int),
        13: ('voucher_per_book', int),
        14: ('barcode_mask', str),
        15: ('voucher_title', str),
        16: ('days_valid', int),
        17: ('ho_compatability_code', str),
        18: ('default_price', float),
        19: ('touch_key', int),
        20: ('print', bool),
        21: ('sst', bool),
        22: ('id', bool),
        23: ('promo', bool),
        24: ('supress_price', bool),
        25: ('allowed_for_no_free_list', bool),
        26: ('allowed_for_restricted_rating', bool),
        27: ('group_ticket', bool),
        28: ('allow_duplicate_barcode', bool),
        29: ('force_receipt', bool),
        30: ('corporate_voucher', bool),
        31: ('allow_default_price', bool),
        33: ('special_action', int),
        34: ('sale_category', int),
        35: ('tax_status', int),
        36: ('tax_rate', float),
        37: ('gl_reference_code', int),
        38: ('gateway_index', int),
        39: ('postcode_sort_code', int),
        40: ('allowed_for_sale_on_web', bool),
        41: ('link_code', int),
        43: ('link_quantity', int),
        44: ('wand_barcode_range', bool),
        45: ('aux_1', int),
        46: ('aux_2', str),
        47: ('venue_class', int),
        48: ('agent_id', int),
        49: ('default_voucher_code', str),
        50: ('revenue_centre_type', int),
        51: ('specified_revenue_centre', int),
        52: ('bypass_online_barcode_check', bool),
        53: ('is_gift_card_sale', bool),
        54: ('ho_lock', bool),
        55: ('ho_price_lock', bool),
        56: ('abc_reference', int),
        57: ('member_bonus_points', bool),
        58: ('force_barcode_capture', bool),
        59: ('print_voucher_slips', bool),
        60: ('is_gift_or_stored_value_card_credit', bool),
        61: ('capture_member_details', bool),
        62: ('member_program_name', str),
        63: ('check_for_membership', bool),
        64: ('force_membership', bool),
        65: ('upsell_ticket_code', str),
        66: ('upsell_ticket_quantity', int),
        67: ('upsell_plu', int),
        68: ('upsell_plu_quantity', int),
        69: ('upsell_plu_price', float),
        70: ('upsell_plu_uom', str),
        71: ('link_plu', int),
        72: ('link_plu_quantity', int),
        73: ('membership_renewal', bool)},
    'vch': {
        2: ('name', str),
        3: ('code', str),
        4: ('text_line_1', str),
        5: ('text_line_2', str),
        6: ('text_line_3', str),
        7: ('text_line_4', str),
        8: ('text_line_5', str),
        9: ('commencement_date', str),
        10: ('expiry_date', str),
        11: ('days_valid', int),
        12: ('valid_immediately', bool),
        13: ('redemption_expiry_date', str),
        14: ('redemption_expiry_type', int),  # 0=Variable, 1=Fixed, 2=No expiry
        15: ('movie_filter', str),
        16: ('venue_class_filter', int),
        18: ('print_barcode', bool),
        19: ('barcode_to_print', str),
        20: ('is_parking_voucher', bool),
        21: ('before_session_parking_buffer_minutes', int),
        22: ('after_session_parking_buffer_minutes', int),
        23: ('use_special_title', bool),
        24: ('special_title', str)},
    'prg': {
        1: ('id', int),
        3: ('name', str),
        4: ('code', str),
        10: ('fee_per_ticket', float),
        11: ('ticket_fee_type', int),
        12: ('fee_per_transaction', float),
        13: ('transaction_fee_type', int),
        14: ('enabled', bool),
        17: ('is_3d_price_group', bool),
        18: ('highlight_price_group_class_in_advertising_display', bool),
        19: ('price_group_class', str),
        20: ('prompt_to_use_upon_session_entry', str),
        21: ('ticket_code_used_with_entry_prompt', str),
        22: ('online_menu', str)},
    'prl': {
        1: ('price_group_code', str),
        2: ('ticket_code', str),
        3: ('voucher_code', str),
        4: ('price', float),
        5: ('valid', bool),
        6: ('surcharge', float),
        7: ('link_ticket_code', str),
        8: ('link_plu', int)},
    'ssn': {
        1: ('session_number', int),
        3: ('cancelled', bool),
        4: ('venue_code', str),
        5: ('movie_code', str),
        6: ('price_group_code', str),
        7: ('reserved', str),
        8: ('start_time', str),
        9: ('accounting_date', str),
        11: ('trailers', int),
        12: ('print', int),
        13: ('category', int),  # 0=Normal, 1=Preview, 2=Local sales only, 3=No sales permitted
        14: ('head_office_code', int),
        15: ('map_code', int),
        17: ('sales_transactions', int),
        18: ('seats_sold', int),
        19: ('sales', float),
        20: ('tax_from_sales', float),
        21: ('refund_transactions', int),
        22: ('seats_credited', int),
        23: ('refunds', float),
        24: ('tax_refunded', float),
        25: ('seats_held_in_unpaid_bookings', int),
        26: ('session_type', int),  # 0=Undefined, 1=Cinema, 2=Exhibition, 3=Theatre, 4=Sport, 5=Tourism, 6=Transport
        27: ('programming_grid_band', int),
        28: ('enterprise_id', int),
        29: ('level', int),  # 0=Normal, 1=MultiLevelPrimary, 2=MultiLevelSecondary
        30: ('plan_code', str),
        31: ('parent_id', int),
        32: ('initial_seats', int),
        33: ('supress_signage', bool),
        34: ('supress_external_services', bool),
        35: ('supress_start_time', bool),
        36: ('supress_advertising', bool),
        37: ('group_booking_type', int),
        38: ('notes', str),
        40: ('programmer_reference', str),
        41: ('venue_class', int),
        42: ('creation_datetime', str),
        43: ('last_modified_datetime', str),
        44: ('modified_by', str),
        45: ('times_modified', int),
        50: ('seats_available_to_3rd_party', int),
        51: ('is_rainout', bool),
        52: ('admission_time', str),
        53: ('admissions', int),
        54: ('web_allocation', int),
        55: ('seats_sold_at_box_office', int),
        56: ('sales_at_box_office', float),
        57: ('seats_sold_at_candy_bar', int),
        58: ('sales_at_candy_bar', float),
        59: ('seats_sold_at_web', int),
        60: ('sales_at_web', float),
        61: ('seats_sold_at_kiosk', int),
        62: ('sales_at_kiosk', float),
        101: ('url', str)},
    'vnc': {
        1: ('index', int),
        2: ('class_name', str),
        3: ('colour', int)},
    'ven': {
        1: ('id', int),
        2: ('venue_name', str),
        3: ('code', str),
        4: ('normal_capacity', int),
        5: ('house_capacity', int),
        6: ('venue_number', int),
        7: ('owner_code', str),
        8: ('venue_class', int),
        9: ('comment', str),
        14: ('default_session_type', int),  # 0=Undefined, 1=Cinema, 2=Exhibition, 3=Theatre, 4=Sport, 5=Tourism, 6=Transport
        15: ('enterprise_id', int),
        16: ('default_session_level', int),  # 0=Normal, 1=MultiLevelPrimary, 2=MultiLevelSecondary
        17: ('parent_code', str),
        18: ('screen_number', int),
        19: ('grid_position', int),
        20: ('premium_venue', bool),
        21: ('hearing_support', bool),
        22: ('map_type', int),
        23: ('default_plan_code', str),
        24: ('handout_advice', str),
        25: ('programming_info', str),
        26: ('colour', int),
        27: ('site_name', str),
        28: ('revenue_centre', int),
        30: ('digital_projection', bool),
        31: ('digital_sound', bool),
        32: ('entry_time', int),  # minutes prior to session
        33: ('display_door_message_on_tickets', bool),
        34: ('venue_class_name', str),
        35: ('lounge_master_code', str)},
    'q02': {
        1: ('detail_required', int)
    },
    'q17': {
        1: ('session_number', int),
        2: ('workstation_id', int)
    },
    'q20': {
        1: ('session_number', int),
        2: ('availability', int)
    },
    'q30': {
        1: ('workstation_id', int),
        2: ('user_code', str),
        3: ('session_number', int),
        4: ('transaction_type', int),  # 0=sale, 1=paid booking
        5: ('customer_reference', str),
        10: ('total_ticket_prices', float),  # ex fees
        11: ('total_ticket_fees', float),
        12: ('transaction_service_fee', float),
        13: ('total_transaction_price', float),
        14: ('total_rainout_amount', float),
        15: ('loyalty_card_number', str),
        16: ('booking_notes', str),
        2001: ('patron_first_name', str),
        2002: ('patron_second_name', str),
        2003: ('patron_email_address', str),
        2004: ('patron_contact_phone_number', str),
        2005: ('opt_out_1', bool),
        2006: ('opt_out_2', bool),
        2007: ('opt_out_3', bool),
        100001: ('ticket_count', int)
    },
    'p30': {
        2: ('seats_split', bool),
        3: ('venue_code', str),
        4: ('venue_name', str),
        5: ('movie_code', str),
        6: ('movie_name', str),
        7: ('session_start_time', str),
        8: ('transaction_fee', float),
        9: ('total_ticket_fees', float),
        10: ('total_transaction_price', float),
        100001: ('ticket_count', int)
    },
    'q31': {
        2: ('workstation_id', int),
        3: ('external_transaction_reference', str),
        4: ('total_amount_paid', float),
        5: ('booking_key', str),  # required
        6: ('booking_name', str),
        7: ('customer_phone_number', str),  # required for all web applications
        8: ('payment_surcharge', float),
        11: ('origin_label', str),  # WWW, IOS, AND, OTH
        # Optional fulfilment information
        51: ('name', str),
        52: ('email_address', str),
        53: ('message', str),
        # Patron information
        2001: ('patron_first_name', str),
        2002: ('patron_second_name', str),
        2003: ('patron_email_address', str),
        2004: ('patron_contact_phone_number', str),
        2005: ('opt_out_1', bool),
        2006: ('opt_out_2', bool),
        2007: ('opt_out_3', bool),
        1001: ('payment_count', int)
    },
    'p31': {
        1: ('booking_index', int),
        2: ('transaction_number', int),
        3: ('key', str),
        4: ('alternate_key', str),
        5: ('pin', int),
        6: ('ticket_message', str),
        100001: ('ticket_count', int)
    },
    'q32': {
        1: ('key', int),
        2: ('use_alternate_key', bool)
    },
    'p32': {
        1: ('session_number', int),
        3: ('venue_code', str),
        4: ('venue_name', str),
        5: ('movie_code', str),
        6: ('movie_name', str),
        7: ('start_time', str),
        100001: ('ticket_count', int)
    },
    'q42': {
        1: ('alternate_booking_key', str)
    },
    'p42': {
        1: ('booking_index', int),
        2: ('transaction_number', int),
        3: ('key', str),
        4: ('alternate_booking_key', str),
        5: ('number_of_tickets', int),
        6: ('number_of_seats', int),
        7: ('transaction_fee', float),
        8: ('total_ticket_fees', float),
        9: ('total_transaction_price', float),
        10: ('session_number', int),
        11: ('customer_reference', str)
    },
    'kyl': {},
    'mky': {}
}  # type: Dict[str, Dict[int, Tuple]]


TICKET_ARRAY_FIELD_MAP = {
    'q30': {
        1: ('ticket_code', str),
        2: ('ticket_price', float),
        3: ('ticket_service_fee', float),
        4: ('seat_name', str),
        5: ('barcode', str),
        6: ('converted_rainout_voucher', bool)
    },
    'p30': {
        1: ('ticket_code', str),
        2: ('companion_voucher_code', str),
        3: ('ticket_price', float),
        4: ('sale_category', int),
        5: ('seat_name', str),
        6: ('ticket_name', str),
        7: ('ticket_number', int),
        8: ('ticket_service_fee', float),
        9: ('ticket_surcharge', float),
        10: ('ticket_barcode', str),
        11: ('voucher_barcode', str),
        12: ('converted_from_voucher', bool),
        13: ('inserted_record', bool)
    }
}  # type: Dict[str, Dict[int, Tuple]]
TICKET_ARRAY_FIELD_MAP['p31'] = TICKET_ARRAY_FIELD_MAP['p30']
TICKET_ARRAY_FIELD_MAP['p32'] = TICKET_ARRAY_FIELD_MAP['p30']

PAYMENT_ARRAY_FIELD_MAP = {
    'q31': {
        1: ('payment_category', int),  # 1=Offline Credit Card; 2=Integrated pinpad online to bank; 4=Credit Card API Gateway; 8=Account; 13=Gift Card API Gateway; 14=Micropayment
        2: ('payment_provider', str),
        3: ('amount_paid', float),
        4: ('card_number', str),
        5: ('cvv_number', str),
        6: ('cardholder_name', str),
        7: ('card_type_name', str),  # e.g. VISA
        8: ('expiry', str),  # MMYY
        9: ('transaction_id', str),
        10: ('authorisation_number', str),  # for offline transactions
        11: ('card_type', int),
        12: ('eft_response', str),
        13: ('lane_number', int),
        14: ('device_id', str),
        15: ('settlement_date', str),
        16: ('voucher_id', str)  # 0=Unknown/na; 1=Visa; 2=MasterCard; 3=Diners; 4=Amex; 5=Bank Card; 6=Gift Card; 7=Debit Card; 8=JCB; 9=Private Label; 10=Other
    }
}  # type: Dict[str, Dict[int, Tuple]]
