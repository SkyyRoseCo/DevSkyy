'use client';

import { useQuery } from '@tanstack/react-query';
import { motion } from 'motion/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Users, Plus, Star, Sparkles, Quote } from 'lucide-react';
import { eliteStudioClient, type Character } from '@/lib/elite-studio-client';
import { ErrorState } from '@/components/shared';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.07 } },
};
const itemVariants = {
  hidden: { y: 12, opacity: 0 },
  visible: { y: 0, opacity: 1 },
};

function CharacterCard({ character, isFeatured = false }: { character: Character; isFeatured?: boolean }) {
  return (
    <motion.div variants={itemVariants}>
      <Card
        className={`h-full transition-all duration-200 ${
          isFeatured
            ? 'bg-gradient-to-br from-[#B76E79]/20 via-gray-900 to-[#D4AF37]/10 border-[#B76E79]/40 hover:border-[#B76E79]/70'
            : 'bg-gray-900 border-gray-800 hover:border-[#B76E79]/30'
        }`}
      >
        <CardHeader>
          <div className='flex items-start justify-between gap-3'>
            <div className='flex items-center gap-3'>
              {/* Avatar placeholder */}
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-xl text-lg font-bold ${
                  isFeatured ? 'bg-gradient-to-br from-[#B76E79] to-[#D4AF37] text-white' : 'bg-gray-800 text-gray-300'
                }`}
                aria-hidden='true'
              >
                {character.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <div className='flex items-center gap-2'>
                  <CardTitle className='text-white text-base'>{character.name}</CardTitle>
                  {isFeatured && (
                    <Star className='h-3.5 w-3.5 text-[#D4AF37] fill-[#D4AF37]' aria-label='Featured character' />
                  )}
                </div>
                <Badge
                  variant='outline'
                  className={`mt-1 text-xs capitalize ${
                    isFeatured ? 'border-[#B76E79]/40 text-[#B76E79]' : 'border-gray-700 text-gray-400'
                  }`}
                >
                  {character.style}
                </Badge>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className='space-y-4'>
          {/* Front view prompt */}
          <div>
            <p className='text-xs text-gray-500 uppercase tracking-wide mb-1.5 flex items-center gap-1.5'>
              <Quote className='h-3 w-3' aria-hidden='true' />
              Front View Prompt
            </p>
            <p className='text-sm text-gray-300 leading-relaxed line-clamp-4'>{character.front_view_prompt}</p>
          </div>

          {/* Sprite description */}
          {character.sprite_description && (
            <div>
              <p className='text-xs text-gray-500 uppercase tracking-wide mb-1.5'>Sprite Description</p>
              <p className='text-xs text-gray-500 leading-relaxed line-clamp-3'>{character.sprite_description}</p>
            </div>
          )}

          {/* Character ID */}
          <div className='pt-2 border-t border-gray-800'>
            <p className='text-xs text-gray-600 font-mono truncate'>{character.character_id}</p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export default function CharactersPage() {
  const {
    data: characters = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['elite-studio', 'characters'],
    queryFn: () => eliteStudioClient.listCharacters(),
    retry: 1,
    staleTime: 30_000,
  });

  const { data: rosie, isLoading: rosieLoading } = useQuery({
    queryKey: ['elite-studio', 'characters', 'rosie'],
    queryFn: () => eliteStudioClient.getRosie(),
    retry: 1,
    staleTime: 60_000,
  });

  const otherCharacters = rosie ? characters.filter(c => c.character_id !== rosie.character_id) : characters;

  return (
    <motion.div initial='hidden' animate='visible' variants={containerVariants} className='space-y-8'>
      {/* Header */}
      <motion.header variants={itemVariants} className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold text-white'>Characters</h1>
          <p className='text-gray-400 mt-1'>Brand character library for SkyyRose</p>
        </div>
        <Button
          className='bg-gradient-to-r from-[#B76E79] to-[#D4AF37] text-white hover:opacity-90 transition-opacity'
          aria-label='Create new character'
        >
          <Plus className='h-4 w-4 mr-2' aria-hidden='true' />
          Create Character
        </Button>
      </motion.header>

      {/* Meet Rosie featured card */}
      <motion.section variants={itemVariants} aria-label='SkyyRose Mascot'>
        <div className='rounded-2xl border border-[#B76E79]/30 bg-gradient-to-r from-[#B76E79]/10 via-gray-900 to-[#D4AF37]/10 p-6'>
          <div className='flex flex-col sm:flex-row items-start sm:items-center gap-6'>
            <div className='flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-[#B76E79] to-[#D4AF37] shrink-0'>
              <Sparkles className='h-9 w-9 text-white' aria-hidden='true' />
            </div>
            <div className='flex-1'>
              <div className='flex items-center gap-2 mb-1'>
                <h2 className='text-xl font-bold text-white'>Meet Rosie</h2>
                <Badge className='bg-[#B76E79]/20 text-[#B76E79] border-[#B76E79]/40 border text-xs'>
                  Brand Mascot
                </Badge>
              </div>
              <p className='text-gray-300 text-sm leading-relaxed max-w-2xl'>
                Rosie is the official SkyyRose mascot — a Pixar-quality character that embodies the brand&apos;s spirit
                of luxury growing from concrete. She appears across all collections as a hidden easter egg in immersive
                world experiences.
              </p>
              {rosie && (
                <div className='mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3'>
                  <div>
                    <p className='text-xs text-gray-500 uppercase tracking-wide mb-1'>Style</p>
                    <Badge variant='outline' className='border-[#B76E79]/40 text-[#B76E79] capitalize text-xs'>
                      {rosie.style}
                    </Badge>
                  </div>
                  <div>
                    <p className='text-xs text-gray-500 uppercase tracking-wide mb-1'>Character ID</p>
                    <p className='text-xs font-mono text-gray-500 truncate'>{rosie.character_id}</p>
                  </div>
                </div>
              )}
              {rosieLoading && (
                <div className='mt-3 space-y-2'>
                  <Skeleton className='h-4 w-32 bg-gray-800' />
                  <Skeleton className='h-4 w-48 bg-gray-800' />
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.section>

      {/* Character grid */}
      <motion.section variants={itemVariants} aria-label='Character library'>
        <div className='flex items-center justify-between mb-4'>
          <h2 className='text-lg font-semibold text-white flex items-center gap-2'>
            <Users className='h-5 w-5 text-[#B76E79]' aria-hidden='true' />
            All Characters
            {!isLoading && (
              <Badge variant='outline' className='border-gray-700 text-gray-400 text-xs'>
                {characters.length}
              </Badge>
            )}
          </h2>
        </div>

        {isLoading ? (
          <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className='h-64 w-full bg-gray-800 rounded-xl' />
            ))}
          </div>
        ) : error ? (
          <ErrorState
            title='Failed to load characters'
            message='Could not reach the Elite Studio API.'
            onRetry={refetch}
          />
        ) : otherCharacters.length === 0 && !rosie ? (
          <Card className='bg-gray-900 border-gray-800'>
            <CardContent className='flex flex-col items-center justify-center py-16 text-center'>
              <Users className='h-12 w-12 text-gray-700 mb-4' aria-hidden='true' />
              <p className='text-gray-400 font-medium'>No characters yet</p>
              <p className='text-gray-600 text-sm mt-1'>Create your first character to see it here.</p>
              <Button
                className='mt-4 bg-gradient-to-r from-[#B76E79] to-[#D4AF37] text-white hover:opacity-90'
                aria-label='Create first character'
              >
                <Plus className='h-4 w-4 mr-2' aria-hidden='true' />
                Create Character
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
            {rosie && !otherCharacters.find(c => c.character_id === rosie.character_id) && (
              <CharacterCard character={rosie} isFeatured />
            )}
            {otherCharacters.map(character => (
              <CharacterCard key={character.character_id} character={character} />
            ))}
          </div>
        )}
      </motion.section>
    </motion.div>
  );
}
