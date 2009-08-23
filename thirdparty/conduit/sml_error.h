/*
 * libsyncml - A syncml protocol implementation
 * Copyright (C) 2005  Armin Bauer <armin.bauer@opensync.org>
 * Copyright (C) 2007-2008  Michael Bell <michael.bell@opensync.org>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
 *
 */

#ifndef _SML_ERROR_H_
#define _SML_ERROR_H_

typedef enum {
	SML_ERRORCLASS_UNKNOWN = 0,
	SML_ERRORCLASS_SUCCESS = 2,
	SML_ERRORCLASS_RETRY = 3,
	SML_ERRORCLASS_FATAL = 5
} SmlErrorClass;

/*! @ingroup smlErrorAPI
 * @brief Defines the possible error types
 */
typedef enum {
	SML_ERROR_UNKNOWN = 0,
	
	/* Informational */
	SML_IN_PROGRESS = 101,
	
	/* OK code */
	/** No error */
	SML_NO_ERROR = 200,
	/** Requested item was added */
	SML_ITEM_ADDED = 201,
	/** Accepted for processing */
	SML_PROCESSING_ACCEPTED = 202,
	/** Non-authoritative response */
	SML_NON_AUTHORITATIVE = 203,
	/** No content */
	SML_NO_CONTENT = 204,
	/** Reset content */
	SML_RESET_CONTENT = 205,
	/** Partial content */
	SML_PARTIAL_CONTENT = 206,
	/** Conflict resolved with merge */
	SML_CONFLICT_MERGE = 207,
	/** Conflict resolved with client win */
	SML_CONFLICT_CLIENT_WIN = 208,
	/** Conflict resolved with duplicate */
	SML_CONFLICT_DUPLICATE = 209,
	/** Deleted without archiving */
	SML_DELETE_NO_ARCHIVE = 210,
	/** Item not deleted (not found) */
	SML_DELETE_NOT_FOUND = 211,
	/** Authentication accepted */
	SML_AUTH_ACCEPTED = 212,
	/** Chunked item accepted */
	SML_CHUNK_ACCEPTED = 213,
	/** Operation cancelled */
	SML_OPERATION_CANCELLED = 214,
	/** Not executed */
	SML_NOT_EXECUTED = 215,
	/** Atomic rollback ok */
	SML_ATOMIC_ROLLBACK_OK = 216,
	
	/* Retry error */
	SML_ERROR_MULTIPLE_CHOICES = 300,
	SML_ERROR_MOVED_PERMANENTLY = 301,
	SML_ERROR_FOUND_RETRY = 302,
	SML_ERROR_SEE_OTHER_RETRY = 303,
	SML_ERROR_NOT_MODIFIED = 304,
	SML_ERROR_USE_PROXY = 305,
	
	/* Errors */
	SML_ERROR_BAD_REQUEST = 400,		// Bad Request
	SML_ERROR_AUTH_REJECTED = 401,		// Unauthorized, Invalid Credentials
	SML_ERROR_PAYMENT_NEEDED =402,		// Payment need
	SML_ERROR_FORBIDDEN = 403,		// Forbidden
	SML_ERROR_NOT_FOUND = 404,		// Not found
	SML_ERROR_COMMAND_NOT_ALLOWED = 405,	// Command not allowed
	SML_ERROR_UNSUPPORTED_FEATURE = 406,	// Optional feature unsupported
	SML_ERROR_AUTH_REQUIRED = 407,		// Authentication required, Missing Credentials
	SML_ERROR_RETRY_LATER = 417,		// Retry later
	SML_ERROR_ALREADY_EXISTS = 418,		// Put or Add failed because item already exists
	SML_ERROR_SIZE_MISMATCH = 424,		// Size mismatch
	
	/* Standard errors */
	SML_ERROR_GENERIC = 500,
	SML_ERROR_NOT_IMPLEMENTED = 501,
	SML_ERROR_SERVICE_UNAVAILABLE = 503,
	SML_ERROR_REQUIRE_REFRESH = 508,
	SML_ERROR_SERVER_FAILURE = 511,

	/* Internal errors - never ever send this via SyncML */
	SML_ERROR_INTERNAL_IO_ERROR = 1501,
	SML_ERROR_INTERNAL_TIMEOUT = 1503,
	SML_ERROR_INTERNAL_FILE_NOT_FOUND = 1505,
	SML_ERROR_INTERNAL_MISCONFIGURATION = 1506,
	SML_ERROR_INTERNAL_NO_MEMORY = 1512

} SmlErrorType;

SmlError **smlErrorRef(SmlError **error);
void smlErrorDeref(SmlError **error);
SmlBool smlErrorIsSet(SmlError **error);
void smlErrorSet(SmlError **error, SmlErrorType type, const char *format, ...);
void smlErrorUpdate(SmlError **error, const char *format, ...);
void smlErrorDuplicate(SmlError **target, SmlError **source);
const char *smlErrorPrint(SmlError **error);
SmlErrorType smlErrorGetType(SmlError **error);
void smlErrorSetType(SmlError **error, SmlErrorType type);
SmlErrorClass smlErrorGetClass(SmlError **error);

#endif //_SML_ERROR_H_
