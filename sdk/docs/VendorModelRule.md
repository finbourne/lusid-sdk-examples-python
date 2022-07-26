# VendorModelRule

A rule that identifies the set of preferences to be used for a given library, model and instrument type.  There can be many such rules, though only the first found for a given combination would be used.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**supplier** | **str** | The available values are: Lusid, RefinitivQps, RefinitivTracsWeb, VolMaster, IsdaCds, YieldBook | 
**model_name** | **str** | The vendor library model name | 
**instrument_type** | **str** | The vendor library instrument type | 
**parameters** | **str** | THIS FIELD IS DEPRECATED - use ModelOptions  The set of opaque model parameters, provided as a Json object, that is a string object which will internally be converted to a dictionary of string to object.  Note that this is not intended as the final form of this object. It will be replaced with a more structured object as the set of parameters that are possible is  better understood. | [optional] 
**model_options** | [**ModelOptions**](ModelOptions.md) |  | [optional] 
**instrument_id** | **str** | This field should generally not be required. It indicates a specific case where there is a particular need to make a rule apply to only a single instrument  specified by an identifier on that instrument such as its LUID. One particular example would be to control the behaviour of a look-through portfolio scaling  methodology, such as where there is a mixture of indices and credit-debit portfolios where scaling on the sum of valuation would be deemed incorrectly for one  set but desired in general. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


