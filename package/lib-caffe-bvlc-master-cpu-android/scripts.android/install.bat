@echo off

rem
rem Installation script for CK packages.
rem
rem See CK LICENSE.txt for licensing details.
rem See CK Copyright.txt for copyright details.
rem
rem Developer(s): Grigori Fursin, 2016-2017
rem

rem PACKAGE_DIR
rem INSTALL_DIR

echo **************************************************************
echo Preparing vars for Caffe ...

set CK_OPENMP=-fopenmp
if "%CK_HAS_OPENMP%" == "0" (
  set CK_OPENMP=
)

set EXTRA_FLAGS=

if  "%CK_CPU_ARM_NEON%" == "ON" (
  set EXTRA_FLAGS=%EXTRA_FLAGS% -mfpu=neon
)

if "%CK_CPU_ARM_VFPV3%" == "ON" (
  set EXTRA_FLAGS=%EXTRA_FLAGS% -mfpu=vfpv3
)

set CK_CC_FLAGS_FOR_CMAKE=%CK_CC_FLAGS_FOR_CMAKE% %EXTRA_FLAGS% -I%CK_ENV_LIB_OPENCV_INCLUDE%
set CK_CXX_FLAGS_FOR_CMAKE=%CK_CXX_FLAGS_FOR_CMAKE% %EXTRA_FLAGS% -I%CK_ENV_LIB_OPENCV_INCLUDE%

set CK_CMAKE_EXTRA=%CK_CMAKE_EXTRA% -DCPU_ONLY:BOOL=%CPU_ONLY% ^
 -DCMAKE_SHARED_LINKER_FLAGS="%CK_OPENMP%" ^
 -DCMAKE_EXE_LINKER_FLAGS="%CK_OPENMP%" ^
 -DBLAS=%BLAS_TYPE% ^
 -DUSE_LMDB=%USE_LMDB% ^
 -DUSE_LEVELDB=%USE_LEVELDB% ^
 -DUSE_LMDB=%USE_LMDB% ^
 -DUSE_LEVELDB=%USE_LEVELDB% ^
 -DUSE_HDF5=OFF ^
 -DBUILD_python=OFF ^
 -DBUILD_docs=OFF ^
 -DGFLAGS_INCLUDE_DIR="%CK_ENV_LIB_GFLAGS_INCLUDE%" ^
 -DGFLAGS_LIBRARY="%CK_ENV_LIB_GFLAGS_LIB%\libgflags.a" ^
 -DGLOG_INCLUDE_DIR="%CK_ENV_LIB_GLOG_INCLUDE%" ^
 -DGLOG_LIBRARY="%CK_ENV_LIB_GLOG_LIB%\libglog.a" ^
 -DCMAKE_BUILD_TYPE:STRING=%CMAKE_CONFIG% ^
 -DPROTOBUF_INCLUDE_DIR="%CK_ENV_LIB_PROTOBUF_INCLUDE%" ^
 -DPROTOBUF_LIBRARY="%CK_ENV_LIB_PROTOBUF_LIB%\libprotobuf.a" ^
 -DOpenBLAS_INCLUDE_DIR="%CK_ENV_LIB_OPENBLAS_INCLUDE%" ^
 -DOpenBLAS_LIB="%CK_ENV_LIB_OPENBLAS_LIB%\libopenblas.a" ^
 -DBoost_ADDITIONAL_VERSIONS="1.62" ^
 -DBoost_NO_SYSTEM_PATHS=ON ^
 -DBOOST_ROOT=%CK_ENV_LIB_BOOST% ^
 -DBOOST_INCLUDEDIR="%CK_ENV_LIB_BOOST_INCLUDE%" ^
 -DBOOST_LIBRARYDIR="%CK_ENV_LIB_BOOST_LIB%" ^
 -DBoost_INCLUDE_DIR="%CK_ENV_LIB_BOOST_INCLUDE%" ^
 -DBoost_LIBRARY_DIR="%CK_ENV_LIB_BOOST_LIB%" ^
 -DBoost_USE_STATIC_LIBS=ON ^
 -DANDROID_NATIVE_API_LEVEL=%CK_ANDROID_API_LEVEL% ^
 -DANDROID_NDK_ABI_NAME="%CK_ANDROID_ABI%" ^
 -DANDROID=ON ^
 -DANDROID_NATIVE_API_LEVEL=%CK_ANDROID_API_LEVEL% ^
 -DANDROID_NDK_ABI_NAME=%CK_ANDROID_ABI% ^
 -DOpenCV_DIR="%CK_ENV_LIB_OPENCV_JNI%" 

rem -DCMAKE_SYSTEM="%CK_ANDROID_NDK_PLATFORM%" ^
rem -DCMAKE_SYSTEM_NAME="Android" ^
rem -DCMAKE_SYSTEM_PROCESSOR="%CK_CMAKE_SYSTEM_PROCESSOR%" ^
rem -DCMAKE_CROSSCOMPILING=TRUE ^
rem -DCMAKE_RC_COMPILER="%CK_CXX%" ^



exit /b 0
