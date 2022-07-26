# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.4620
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from lusid.configuration import Configuration


class DataDefinition(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
      required_map (dict): The key is attribute name
                           and the value is whether it is 'required' or 'optional'.
    """
    openapi_types = {
        'address': 'str',
        'name': 'str',
        'data_type': 'str',
        'key_type': 'str',
        'allow_null': 'bool',
        'allow_missing': 'bool'
    }

    attribute_map = {
        'address': 'address',
        'name': 'name',
        'data_type': 'dataType',
        'key_type': 'keyType',
        'allow_null': 'allowNull',
        'allow_missing': 'allowMissing'
    }

    required_map = {
        'address': 'optional',
        'name': 'optional',
        'data_type': 'optional',
        'key_type': 'optional',
        'allow_null': 'optional',
        'allow_missing': 'optional'
    }

    def __init__(self, address=None, name=None, data_type=None, key_type=None, allow_null=None, allow_missing=None, local_vars_configuration=None):  # noqa: E501
        """DataDefinition - a model defined in OpenAPI"
        
        :param address:  The internal address (LUSID native) of the unit in the provided data itself and corresponds to the external name of the data item
        :type address: str
        :param name:  The name of the data item. This is the name that will appear
        :type name: str
        :param data_type:  A member of the set of possible data types, that all data passed under that key is expected to be of.  Currently limited to one of [string, integer, decimal, result0d].
        :type data_type: str
        :param key_type:  Is the item either a unique key for the dictionary, i.e. does it identify a unique index or conceptual 'row' within the list of dictionaries,  or a partial key or is it simply a data item within that dictionary. Must be one of [Unique,PartOfUnique,Leaf, CompositeLeaf]
        :type key_type: str
        :param allow_null:  The path to the field must exist (unless AllowMissing is true) but the actual value is allowed to be null.
        :type allow_null: bool
        :param allow_missing:  The path (or column) is allowed to be missing but if it is present it is not allowed to be null unless AllowNull is true.
        :type allow_missing: bool

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._address = None
        self._name = None
        self._data_type = None
        self._key_type = None
        self._allow_null = None
        self._allow_missing = None
        self.discriminator = None

        self.address = address
        self.name = name
        self.data_type = data_type
        self.key_type = key_type
        if allow_null is not None:
            self.allow_null = allow_null
        if allow_missing is not None:
            self.allow_missing = allow_missing

    @property
    def address(self):
        """Gets the address of this DataDefinition.  # noqa: E501

        The internal address (LUSID native) of the unit in the provided data itself and corresponds to the external name of the data item  # noqa: E501

        :return: The address of this DataDefinition.  # noqa: E501
        :rtype: str
        """
        return self._address

    @address.setter
    def address(self, address):
        """Sets the address of this DataDefinition.

        The internal address (LUSID native) of the unit in the provided data itself and corresponds to the external name of the data item  # noqa: E501

        :param address: The address of this DataDefinition.  # noqa: E501
        :type address: str
        """

        self._address = address

    @property
    def name(self):
        """Gets the name of this DataDefinition.  # noqa: E501

        The name of the data item. This is the name that will appear  # noqa: E501

        :return: The name of this DataDefinition.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this DataDefinition.

        The name of the data item. This is the name that will appear  # noqa: E501

        :param name: The name of this DataDefinition.  # noqa: E501
        :type name: str
        """
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) > 256):
            raise ValueError("Invalid value for `name`, length must be less than or equal to `256`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) < 1):
            raise ValueError("Invalid value for `name`, length must be greater than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                name is not None and not re.search(r'^[a-zA-Z0-9\-_]+$', name)):  # noqa: E501
            raise ValueError(r"Invalid value for `name`, must be a follow pattern or equal to `/^[a-zA-Z0-9\-_]+$/`")  # noqa: E501

        self._name = name

    @property
    def data_type(self):
        """Gets the data_type of this DataDefinition.  # noqa: E501

        A member of the set of possible data types, that all data passed under that key is expected to be of.  Currently limited to one of [string, integer, decimal, result0d].  # noqa: E501

        :return: The data_type of this DataDefinition.  # noqa: E501
        :rtype: str
        """
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        """Sets the data_type of this DataDefinition.

        A member of the set of possible data types, that all data passed under that key is expected to be of.  Currently limited to one of [string, integer, decimal, result0d].  # noqa: E501

        :param data_type: The data_type of this DataDefinition.  # noqa: E501
        :type data_type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                data_type is not None and len(data_type) > 128):
            raise ValueError("Invalid value for `data_type`, length must be less than or equal to `128`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                data_type is not None and len(data_type) < 0):
            raise ValueError("Invalid value for `data_type`, length must be greater than or equal to `0`")  # noqa: E501

        self._data_type = data_type

    @property
    def key_type(self):
        """Gets the key_type of this DataDefinition.  # noqa: E501

        Is the item either a unique key for the dictionary, i.e. does it identify a unique index or conceptual 'row' within the list of dictionaries,  or a partial key or is it simply a data item within that dictionary. Must be one of [Unique,PartOfUnique,Leaf, CompositeLeaf]  # noqa: E501

        :return: The key_type of this DataDefinition.  # noqa: E501
        :rtype: str
        """
        return self._key_type

    @key_type.setter
    def key_type(self, key_type):
        """Sets the key_type of this DataDefinition.

        Is the item either a unique key for the dictionary, i.e. does it identify a unique index or conceptual 'row' within the list of dictionaries,  or a partial key or is it simply a data item within that dictionary. Must be one of [Unique,PartOfUnique,Leaf, CompositeLeaf]  # noqa: E501

        :param key_type: The key_type of this DataDefinition.  # noqa: E501
        :type key_type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                key_type is not None and len(key_type) > 128):
            raise ValueError("Invalid value for `key_type`, length must be less than or equal to `128`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                key_type is not None and len(key_type) < 0):
            raise ValueError("Invalid value for `key_type`, length must be greater than or equal to `0`")  # noqa: E501

        self._key_type = key_type

    @property
    def allow_null(self):
        """Gets the allow_null of this DataDefinition.  # noqa: E501

        The path to the field must exist (unless AllowMissing is true) but the actual value is allowed to be null.  # noqa: E501

        :return: The allow_null of this DataDefinition.  # noqa: E501
        :rtype: bool
        """
        return self._allow_null

    @allow_null.setter
    def allow_null(self, allow_null):
        """Sets the allow_null of this DataDefinition.

        The path to the field must exist (unless AllowMissing is true) but the actual value is allowed to be null.  # noqa: E501

        :param allow_null: The allow_null of this DataDefinition.  # noqa: E501
        :type allow_null: bool
        """

        self._allow_null = allow_null

    @property
    def allow_missing(self):
        """Gets the allow_missing of this DataDefinition.  # noqa: E501

        The path (or column) is allowed to be missing but if it is present it is not allowed to be null unless AllowNull is true.  # noqa: E501

        :return: The allow_missing of this DataDefinition.  # noqa: E501
        :rtype: bool
        """
        return self._allow_missing

    @allow_missing.setter
    def allow_missing(self, allow_missing):
        """Sets the allow_missing of this DataDefinition.

        The path (or column) is allowed to be missing but if it is present it is not allowed to be null unless AllowNull is true.  # noqa: E501

        :param allow_missing: The allow_missing of this DataDefinition.  # noqa: E501
        :type allow_missing: bool
        """

        self._allow_missing = allow_missing

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, DataDefinition):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DataDefinition):
            return True

        return self.to_dict() != other.to_dict()
