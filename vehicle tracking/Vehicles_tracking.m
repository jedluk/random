function [] = Vehicles_tracking(movieIn,movieOut,N,windowSize)
%Vehicles_tracking(movieIn,movieOut,N,windowSize) is implementation of vision 
% system to tracking vehicles in movieIn. Method of estimation background: 
% median filter with downsampling. Blobs are tracked as red marker in the movieOut.
%
% Arguments: 
%
% movieIn - name of input movie with extension. File must exists in current 
% folder, and has any format. This argument is required.
% movieOut - name of output movie (freeform), this argument is optional.
% Possible output format is AVI or MPEG-4. Default format is AVI.
% N - number of frames to calculate background after downsampling
% windowSize - amount of frames to calculate background before downsampling
% 
% i.e.
% Vehicles_tracking('input.mp4,'wynik.mp4',10,40) takes input.mp4 as input movie
% and record movie wynik.mp4 where estimate background is median of 10 frames
% out of 40.
% Vehicles_tracking('name.avi') records movie with default name: 'out.avi'
%
% See also MEDIAN , VIDEOREADER, VIDEOWRITER
% 
% Copyright (c): Jêdrzej £ukasiuk

% clear all variables and command window, close all opened windows
%clear all, close all, clc;

% clock start
tic

% check if input file exists
if ( ~(exist(movieIn,'file') == 2))
 warningMessage = sprintf('File does not exist:\n%s', movieIn);
 uiwait(msgbox(warningMessage));
 error('No such file exists');
end

% check number of input arguments
switch(nargin)
    
    case 1 % user specifes only name of input file
        
        movieOut = 'out.avi'; % set default output name
        outMP4 = false; % set default mp4 flag
        N = 10; % set default N value
        windowSize = 20; % set default windowSize
        
    case 2 % user specifies name of input and output files

        % create regex to find extension of file - search for .mp4 or .avi
        pat = '\.(mp4)|(avi)';
        % find extension of file
        out = regexp(movieOut,pat,'match');
        
        if ( strcmp(out,'.mp4') )
            outMP4 = true; % flag for avi format
        else 
            outMP4 = false; 
        end
        
        N = 10; % set default N value
        windowSize = 20; % set default windowSize
        
    case 3 % user specifes name of input and output files, and number of frame
        
        % create regex to find extension of file - search .mp4 or .avi
        pat = '\.(mp4)|(avi)';
        % find extension of file
        out = regexp(movieOut,pat,'match');
        

        if ( strcmp(out,'.mp4') )
            outMP4 = true; % flag for avi format
        else 
            outMP4 = false; 
        end
        
        windowSize = 20; % set default windowSize
        
        
    case 4 % user specifies all arguments
        
        % create regex to find extension of file - search .mp4 or .avi
        pat = '\.(mp4)|(avi)';
        % find extension of file
        out = regexp(movieOut,pat,'match');
        
        if ( strcmp(out,'.mp4') )
            outMP4 = true; % flag for avi format
        else 
            outMP4 = false; 
        end
        
        % check if number of frames is greater than windowSize (incorrect behavior) 
        if ( N > windowSize )
            error('Enter the correct values ( N must be less equal windowSize)');
        end

end

% create new VideoReader object
v = VideoReader(movieIn);
% matrix to stores frames in greyscale
grayFrames = zeros(v.Height,v.Width,v.NumberOfFrames);

% get all frames from movie and convert it to grayscale
for img = 1 : v.NumberOfFrames
    
    tempImg = read(v,img);
    grayFrames(:,:,img) = rgb2gray(tempImg);
    
end


% create VideoWriter
if ( outMP4 ) % if user specified .mp4 in induction
    y = VideoWriter(movieOut,'MPEG-4');
else
    y = VideoWriter(movieOut); % avi is default
end

% open VideoWriter
open(y);
% matrix stores frames to calculate background (before downsampling) 
matBack = zeros(v.Height,v.Width,windowSize);
% matBack after downsampling
matBackDown = zeros(v.Height,v.Width,N);

% X stores all frames used in calculated background in one vector
X = [];
% loop for each frames
for i = (windowSize+1) : v.numberOfFrames
    
    n = 1; % reset the number of frames in background before downsampling
       
    % indexes of N random frames - default choose 10 from 20
    indexes = randperm(windowSize,N); % indexes stores N number of frames
    
    X = [X indexes];
    
    for j = (i-windowSize) : (i-1)
    
        matBack(:,:,n) = grayFrames(:,:,j);
        % next background frame
        n = n+1;
        
    end
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % DOWNSAMPLING - only N frames to calculate background !!!
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    for k = 1:length(indexes)
        
        matBackDown(:,:,k) = matBack(:,:,indexes(k));
          
    end
        
    % calculate temporary background
    tempBackground = median(matBackDown,3);
    
    % current frame
    tempFrame = grayFrames(:,:,i);
    
    % difference beetwen background and current frame
    I = tempFrame - tempBackground;
    
    % absolute value of I - problem with negative values
    I = abs(I);
    
    % hardcoded binarisation 
    BW = I > 60; % try other values
    
    % read original frame
    K = read(v,i);
   
    % some important operation
    for j = 1 : v.Height
        for k = 1 : v.Width
          
            if(BW(j,k) == 1)
                
                % override orignal frame with red marker on blob
                K(j,k,1) = 255;
                K(j,k,2) = 0;
                K(j,k,3) = 0;
               
            end
     
        end
    end    
    
    % write current frame
    writeVideo(y,K);
    
end

% close Wideo Writer
close(y);

% random frames histogram
figure()
hist(X,windowSize)

% clock stop
toc

end